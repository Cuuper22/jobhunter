"""API Gateway — Cloud Run entry point.

Serves as the central API for the React dashboard.
Proxies requests to agent-browser service and manages Firestore state.
"""

import logging
import math
import os
import sys

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_gateway.middleware.auth import verify_firebase_token

from api_gateway.routers import jobs, applications, controls, scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="JobHunter API Gateway")

# CORS for Firebase Hosting frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # local dev
        "https://*.web.app",     # Firebase Hosting
        "https://*.firebaseapp.com",
        "https://dashboard-73685042772.us-central1.run.app",
        "https://*.run.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(controls.router)
app.include_router(scheduler.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.get("/api/stats")
async def stats(user=Depends(verify_firebase_token)):
    """Dashboard summary stats."""
    import asyncio
    from shared.firestore_client import db
    from google.cloud.firestore_v1 import FieldFilter

    def get_count(query):
        return query.count().get()[0][0].value

    # Run all synchronous count queries concurrently in separate threads
    # to avoid blocking the main event loop.
    jobs_count, apps_count, pending_count, submitted_count = await asyncio.gather(
        asyncio.to_thread(get_count, db.collection("jobs")),
        asyncio.to_thread(get_count, db.collection("applications")),
        asyncio.to_thread(get_count, db.collection("applications").where(filter=FieldFilter("status", "==", "pending_approval"))),
        asyncio.to_thread(get_count, db.collection("applications").where(filter=FieldFilter("status", "==", "submitted")))
    )

    return {
        "total_jobs_scraped": jobs_count,
        "total_applications": apps_count,
        "pending_approval": pending_count,
        "submitted": submitted_count,
    }


@app.get("/api/logs")
async def recent_logs(limit: int = 50, user=Depends(verify_firebase_token)):
    """Get recent activity logs for the dashboard log stream."""
    from shared.firestore_client import db

    docs = (
        db.collection("logs")
        .order_by("timestamp", direction="DESCENDING")
        .limit(limit)
        .get()
    )
    return [
        {k: (None if isinstance(v, float) and (math.isnan(v) or math.isinf(v)) else v)
         for k, v in doc.to_dict().items()}
        for doc in docs
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
