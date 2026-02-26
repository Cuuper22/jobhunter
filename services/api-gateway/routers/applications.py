"""Application management endpoints — approve, reject, edit cover letters."""

import math
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud.firestore_v1 import FieldFilter
from pydantic import BaseModel

from shared.firestore_client import db, update_application_status, log
from shared.models import ApplicationStatus, LogLevel
from api_gateway.middleware.auth import verify_firebase_token


def _sanitize(doc: dict) -> dict:
    """Replace NaN/Inf floats with None for JSON compliance."""
    return {
        k: (None if isinstance(v, float) and (math.isnan(v) or math.isinf(v)) else v)
        for k, v in doc.items()
    }

router = APIRouter(prefix="/api/applications", tags=["applications"])


class ApproveRequest(BaseModel):
    edited_cover_letter: str | None = None


class RejectRequest(BaseModel):
    reason: str = ""


class UpdateApplicationRequest(BaseModel):
    cover_letter: str | None = None
    cover_letter_edited: str | None = None
    form_data: dict | None = None
    outreach_subject: str | None = None
    outreach_email: str | None = None


@router.get("/")
async def list_applications(
    status: str | None = None,
    limit: int = Query(50, le=200),
    user=Depends(verify_firebase_token),
):
    """List applications, optionally filtered by status."""
    query = db.collection("applications").order_by("created_at", direction="DESCENDING")

    if status:
        query = query.where(filter=FieldFilter("status", "==", status))

    docs = query.limit(limit).get()
    return [_sanitize(doc.to_dict()) for doc in docs]


@router.get("/pending")
async def list_pending(user=Depends(verify_firebase_token)):
    """Get all applications awaiting approval."""
    docs = (
        db.collection("applications")
        .where(filter=FieldFilter("status", "==", ApplicationStatus.PENDING_APPROVAL.value))
        .order_by("created_at")
        .get()
    )
    return [_sanitize(doc.to_dict()) for doc in docs]


@router.get("/{app_id}")
async def get_application(app_id: str, user=Depends(verify_firebase_token)):
    doc = db.collection("applications").document(app_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Application not found")
    return _sanitize(doc.to_dict())


@router.patch("/{app_id}")
async def update_application(
    app_id: str,
    req: UpdateApplicationRequest,
    user=Depends(verify_firebase_token),
):
    """Partial update — save edited cover letter, form fields, outreach email before approval."""
    doc = db.collection("applications").document(app_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Application not found")

    updates = {"updated_at": datetime.utcnow().isoformat()}
    # Only include non-None fields
    for field in ["cover_letter", "cover_letter_edited", "form_data", "outreach_subject", "outreach_email"]:
        value = getattr(req, field)
        if value is not None:
            updates[field] = value

    db.collection("applications").document(app_id).update(updates)
    return {"status": "updated", "application_id": app_id, "fields_updated": [k for k in updates if k != "updated_at"]}


@router.post("/{app_id}/approve")
async def approve_application(
    app_id: str,
    req: ApproveRequest,
    user=Depends(verify_firebase_token),
):
    """Approve an application for submission. Optionally update the cover letter."""
    doc = db.collection("applications").document(app_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Application not found")

    data = doc.to_dict()
    if data["status"] != ApplicationStatus.PENDING_APPROVAL.value:
        raise HTTPException(status_code=400, detail=f"Cannot approve: status is {data['status']}")

    extra = {"updated_at": datetime.utcnow().isoformat()}
    if req.edited_cover_letter:
        extra["cover_letter_edited"] = req.edited_cover_letter
        # Update form_data cover letter too
        form_data = data.get("form_data", {})
        form_data["cover_letter"] = req.edited_cover_letter
        extra["form_data"] = form_data

    update_application_status(app_id, ApplicationStatus.APPROVED, **extra)
    log(
        f"Application approved for {data.get('company', '?')}",
        level=LogLevel.SUCCESS,
        application_id=app_id,
    )
    return {"status": "approved", "application_id": app_id}


@router.post("/{app_id}/reject")
async def reject_application(
    app_id: str,
    req: RejectRequest,
    user=Depends(verify_firebase_token),
):
    """Reject an application — skip this job."""
    update_application_status(
        app_id,
        ApplicationStatus.REJECTED_BY_USER,
        error_message=req.reason,
        updated_at=datetime.utcnow().isoformat(),
    )
    log(
        f"Application rejected: {req.reason}",
        level=LogLevel.INFO,
        application_id=app_id,
    )
    return {"status": "rejected", "application_id": app_id}
