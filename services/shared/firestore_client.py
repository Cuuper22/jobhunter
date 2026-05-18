"""Firestore client for reading/writing jobs, applications, and logs."""

import os
from datetime import datetime
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import FieldFilter

from .models import Application, ApplicationStatus, Job, LogEntry, LogLevel


def _init_firebase():
    """Initialize Firebase Admin SDK."""
    if not firebase_admin._apps:
        sa_base64 = os.getenv("FIREBASE_SERVICE_ACCOUNT_BASE64")
        if sa_base64:
            import base64, json, tempfile
            sa_json = base64.b64decode(sa_base64).decode()
            sa_path = tempfile.mktemp(suffix=".json")
            with open(sa_path, "w") as f:
                f.write(sa_json)
            cred = credentials.Certificate(sa_path)
        else:
            # Fall back to Application Default Credentials (local dev / Cloud Run)
            cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)


_init_firebase()
db = firestore.client()


# ---------- Jobs ----------

def save_job(job: Job) -> str:
    """Save a scraped job. Returns the document ID."""
    doc_ref = db.collection("jobs").document()
    job.id = doc_ref.id
    doc_ref.set(job.model_dump(mode="json"))
    return doc_ref.id


def get_job(job_id: str) -> Optional[Job]:
    doc = db.collection("jobs").document(job_id).get()
    return Job(**doc.to_dict()) if doc.exists else None


def bulk_job_exists(urls: set[str]) -> set[str]:
    """Check existence of multiple job URLs (dedup) in chunks of 30."""
    if not urls:
        return set()

    existing = set()
    urls_list = list(urls)

    # Firestore 'in' queries support max 30 items
    chunk_size = 30
    for i in range(0, len(urls_list), chunk_size):
        chunk = urls_list[i:i + chunk_size]
        docs = (
            db.collection("jobs")
            .where(filter=FieldFilter("url", "in", chunk))
            .get()
        )
        for doc in docs:
            existing.add(doc.to_dict().get("url"))

    return existing


def job_exists(url: str) -> bool:
    """Check if a job URL has already been scraped (dedup)."""
    docs = (
        db.collection("jobs")
        .where(filter=FieldFilter("url", "==", url))
        .limit(1)
        .get()
    )
    return len(docs) > 0


def save_jobs_batch(jobs: list[Job]) -> list[str]:
    """Save multiple scraped jobs using batched writes (max 500 per batch)."""
    if not jobs:
        return []

    job_ids = []
    chunk_size = 500

    for i in range(0, len(jobs), chunk_size):
        chunk = jobs[i:i + chunk_size]
        batch = db.batch()

        for job in chunk:
            doc_ref = db.collection("jobs").document()
            job.id = doc_ref.id
            job_ids.append(job.id)
            batch.set(doc_ref, job.model_dump(mode="json"))

        batch.commit()

    return job_ids


def update_job_score(job_id: str, score: int, reasoning: str):
    db.collection("jobs").document(job_id).update({
        "fit_score": score,
        "fit_reasoning": reasoning,
    })


# ---------- Applications ----------

def save_application(app: Application) -> str:
    doc_ref = db.collection("applications").document()
    app.id = doc_ref.id
    doc_ref.set(app.model_dump(mode="json"))
    return doc_ref.id


def get_application(app_id: str) -> Optional[Application]:
    doc = db.collection("applications").document(app_id).get()
    return Application(**doc.to_dict()) if doc.exists else None


def update_application_status(app_id: str, status: ApplicationStatus, **extra):
    data = {"status": status.value, "updated_at": datetime.utcnow().isoformat()}
    data.update(extra)
    db.collection("applications").document(app_id).update(data)


def get_pending_approvals() -> list[Application]:
    docs = (
        db.collection("applications")
        .where(filter=FieldFilter("status", "==", ApplicationStatus.PENDING_APPROVAL.value))
        .order_by("created_at")
        .get()
    )
    return [Application(**d.to_dict()) for d in docs]


def get_approved_applications() -> list[Application]:
    docs = (
        db.collection("applications")
        .where(filter=FieldFilter("status", "==", ApplicationStatus.APPROVED.value))
        .order_by("created_at")
        .get()
    )
    return [Application(**d.to_dict()) for d in docs]


# ---------- Logs ----------

def log(
    message: str,
    level: LogLevel = LogLevel.INFO,
    job_id: Optional[str] = None,
    application_id: Optional[str] = None,
    screenshot_url: Optional[str] = None,
    metadata: Optional[dict] = None,
):
    entry = LogEntry(
        message=message,
        level=level,
        job_id=job_id,
        application_id=application_id,
        screenshot_url=screenshot_url,
        metadata=metadata,
    )
    doc_ref = db.collection("logs").document()
    entry.id = doc_ref.id
    doc_ref.set(entry.model_dump(mode="json"))
    return doc_ref.id
