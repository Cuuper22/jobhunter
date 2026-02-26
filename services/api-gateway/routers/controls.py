"""Emergency controls — pause, resume, purge queue."""

import os

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from shared.firestore_client import log
from shared.models import LogLevel
from api_gateway.middleware.auth import verify_firebase_token

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")

router = APIRouter(prefix="/api/controls", tags=["controls"])


class ControlResponse(BaseModel):
    action: str
    success: bool
    message: str


@router.post("/pause")
async def pause_queue(user=Depends(verify_firebase_token)):
    """Pause the Cloud Tasks queue — stops new scrapes/applications."""
    from google.cloud import tasks_v2

    try:
        client = tasks_v2.CloudTasksClient()
        queue_path = client.queue_path(
            project=PROJECT_ID, location="us-central1", queue="job-applications"
        )
        client.pause_queue(name=queue_path)
        log("Queue paused by user", level=LogLevel.WARNING)
        return ControlResponse(action="pause", success=True, message="Queue paused")
    except Exception as e:
        return ControlResponse(action="pause", success=False, message=str(e))


@router.post("/resume")
async def resume_queue(user=Depends(verify_firebase_token)):
    """Resume the Cloud Tasks queue."""
    from google.cloud import tasks_v2

    try:
        client = tasks_v2.CloudTasksClient()
        queue_path = client.queue_path(
            project=PROJECT_ID, location="us-central1", queue="job-applications"
        )
        client.resume_queue(name=queue_path)
        log("Queue resumed by user", level=LogLevel.INFO)
        return ControlResponse(action="resume", success=True, message="Queue resumed")
    except Exception as e:
        return ControlResponse(action="resume", success=False, message=str(e))


@router.post("/emergency-stop")
async def emergency_stop(user=Depends(verify_firebase_token)):
    """Emergency stop — pause queue AND purge all pending tasks."""
    from google.cloud import tasks_v2

    try:
        client = tasks_v2.CloudTasksClient()
        queue_path = client.queue_path(
            project=PROJECT_ID, location="us-central1", queue="job-applications"
        )
        client.pause_queue(name=queue_path)
        client.purge_queue(name=queue_path)
        log("EMERGENCY STOP: Queue paused and purged", level=LogLevel.ERROR)
        return ControlResponse(
            action="emergency_stop", success=True,
            message="Queue paused and all pending tasks purged",
        )
    except Exception as e:
        return ControlResponse(action="emergency_stop", success=False, message=str(e))
