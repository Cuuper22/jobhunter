"""Cloud Scheduler trigger — proxies scrape-and-process to agent-browser."""

import logging
import os

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from shared.firestore_client import log
from shared.models import LogLevel

logger = logging.getLogger(__name__)

AGENT_BROWSER_URL = os.getenv(
    "AGENT_BROWSER_URL",
    "https://agent-browser-73685042772.us-central1.run.app",
)

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


class TriggerResponse(BaseModel):
    triggered: bool
    message: str
    details: dict | None = None


@router.post("/trigger")
async def trigger_cycle(min_score: int = 40):
    """Trigger a full scrape-and-process cycle on agent-browser.

    Called by Cloud Scheduler or manually via the dashboard.
    Uses service-to-service auth (Cloud Run identity).
    """
    log("Scheduler triggered scrape-and-process cycle", level=LogLevel.INFO)

    try:
        # Get identity token for service-to-service auth
        id_token = _get_id_token(AGENT_BROWSER_URL)

        async with httpx.AsyncClient(timeout=900.0) as client:
            headers = {}
            if id_token:
                headers["Authorization"] = f"Bearer {id_token}"

            resp = await client.post(
                f"{AGENT_BROWSER_URL}/scrape-and-process",
                params={"min_score": min_score},
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        log(
            f"Scheduler cycle complete: {data.get('message', 'done')}",
            level=LogLevel.SUCCESS,
        )
        return TriggerResponse(triggered=True, message="Cycle complete", details=data)

    except Exception as e:
        log(f"Scheduler trigger failed: {e}", level=LogLevel.ERROR)
        return TriggerResponse(triggered=False, message=f"Failed: {e}")


def _get_id_token(audience: str) -> str | None:
    """Get a Google Cloud identity token for service-to-service auth."""
    try:
        import google.auth.transport.requests
        import google.oauth2.id_token

        request = google.auth.transport.requests.Request()
        return google.oauth2.id_token.fetch_id_token(request, audience)
    except Exception:
        # Local dev — no identity token needed
        return None
