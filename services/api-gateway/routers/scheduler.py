"""Cloud Scheduler trigger — fires scrape-and-process on agent-browser."""

import asyncio
import logging
import os

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from shared.firestore_client import log
from shared.models import LogLevel
from api_gateway.middleware.auth import verify_firebase_token

logger = logging.getLogger(__name__)

AGENT_BROWSER_URL = os.getenv(
    "AGENT_BROWSER_URL",
    "https://agent-browser-73685042772.us-central1.run.app",
)

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


class TriggerResponse(BaseModel):
    triggered: bool
    message: str


@router.post("/trigger")
async def trigger_cycle(
    min_score: int = 40,
    user=Depends(verify_firebase_token),
):
    """Trigger a full scrape-and-process cycle on agent-browser.

    Fires the request asynchronously and returns immediately.
    The agent-browser processes in the background (Cloud Run keeps the
    instance alive until the request completes).
    """
    log("Scheduler triggered scrape-and-process cycle", level=LogLevel.INFO)

    # Fire and forget — don't wait for the full cycle
    asyncio.create_task(_fire_cycle(min_score))

    return TriggerResponse(triggered=True, message="Cycle triggered (running in background)")


async def _fire_cycle(min_score: int):
    """Send the request to agent-browser. Runs as background task."""
    try:
        id_token = _get_id_token(AGENT_BROWSER_URL)
        headers = {"Content-Type": "application/json"}
        if id_token:
            headers["Authorization"] = f"Bearer {id_token}"

        async with httpx.AsyncClient(timeout=900.0) as client:
            resp = await client.post(
                f"{AGENT_BROWSER_URL}/scrape-and-process",
                params={"min_score": min_score},
                headers=headers,
                content="{}",
            )
            resp.raise_for_status()
            data = resp.json()

        log(
            f"Scheduler cycle complete: {data.get('message', 'done')}",
            level=LogLevel.SUCCESS,
        )
    except Exception as e:
        log(f"Scheduler cycle failed: {e}", level=LogLevel.ERROR)
        logger.error(f"Scheduler cycle error: {e}")


def _get_id_token(audience: str) -> str | None:
    """Get a Google Cloud identity token for service-to-service auth."""
    try:
        import google.auth.transport.requests
        import google.oauth2.id_token

        request = google.auth.transport.requests.Request()
        return google.oauth2.id_token.fetch_id_token(request, audience)
    except Exception:
        return None
