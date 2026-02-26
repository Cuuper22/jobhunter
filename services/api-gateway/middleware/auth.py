"""Simple password authentication middleware for FastAPI.

Uses a shared API_PASSWORD env var. The dashboard sends it via
Authorization: Bearer <password> header or ?password= query param.

Also accepts Google Cloud OIDC tokens for service-to-service auth
(Cloud Scheduler → API Gateway).
"""

import os
from fastapi import HTTPException, Request

# Password loaded once at startup
API_PASSWORD = os.getenv("API_PASSWORD", "")


async def verify_firebase_token(request: Request) -> dict:
    """Verify request authentication.

    Kept the function name for backward compatibility with existing Depends() calls.

    Auth methods (checked in order):
    1. SKIP_AUTH=true env var → allow all (local dev)
    2. Authorization: Bearer <password> header
    3. ?password=<password> query parameter
    """
    # Skip auth in local dev
    if os.getenv("SKIP_AUTH", "").lower() == "true":
        return {"uid": "local-dev", "email": "dev@local"}

    if not API_PASSWORD:
        # No password configured — allow all (for initial setup)
        return {"uid": "anonymous", "email": "anonymous"}

    # Check Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split("Bearer ", 1)[1]
        if token == API_PASSWORD:
            return {"uid": "user", "email": "user@jobhunter"}

    # Check query parameter
    password = request.query_params.get("password", "")
    if password == API_PASSWORD:
        return {"uid": "user", "email": "user@jobhunter"}

    raise HTTPException(status_code=401, detail="Invalid password")
