"""Job listing endpoints."""

import math

from fastapi import APIRouter, Depends, Query
from google.cloud.firestore_v1 import FieldFilter

from shared.firestore_client import db
from shared.models import Job
from api_gateway.middleware.auth import verify_firebase_token


def _sanitize(doc: dict) -> dict:
    """Replace NaN/Inf floats with None for JSON compliance."""
    return {
        k: (None if isinstance(v, float) and (math.isnan(v) or math.isinf(v)) else v)
        for k, v in doc.items()
    }

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/")
async def list_jobs(
    limit: int = Query(50, le=200),
    min_score: int = Query(0, ge=0, le=100),
    source: str | None = None,
    user=Depends(verify_firebase_token),
):
    """List scraped jobs, optionally filtered by score and source."""
    query = db.collection("jobs").order_by("date_scraped", direction="DESCENDING")

    if min_score > 0:
        query = query.where(filter=FieldFilter("fit_score", ">=", min_score))

    if source:
        query = query.where(filter=FieldFilter("source", "==", source))

    docs = query.limit(limit).get()
    return [_sanitize(doc.to_dict()) for doc in docs]


@router.get("/{job_id}")
async def get_job(job_id: str, user=Depends(verify_firebase_token)):
    """Get a single job by ID."""
    doc = db.collection("jobs").document(job_id).get()
    if not doc.exists:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    return _sanitize(doc.to_dict())
