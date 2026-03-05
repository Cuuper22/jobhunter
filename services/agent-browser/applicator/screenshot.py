"""Capture screenshots of form state before submission."""

import asyncio
import logging
import os
from datetime import datetime

from google.cloud import storage
from playwright.async_api import Page

logger = logging.getLogger(__name__)

BUCKET_NAME = os.getenv("SCREENSHOTS_BUCKET", "")


async def capture_screenshot(page: Page, job_id: str, label: str = "pre_submit") -> str:
    """Take a full-page screenshot and upload to Cloud Storage.

    Args:
        page: Playwright page object
        job_id: Job ID for naming
        label: Description label (e.g., 'pre_submit', 'error')

    Returns:
        Public URL of the uploaded screenshot
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshots/{job_id}/{label}_{timestamp}.png"

    # Capture screenshot bytes
    screenshot_bytes = await page.screenshot(full_page=True)

    if not BUCKET_NAME:
        # Local dev: save to /tmp
        local_path = f"/tmp/{filename.replace('/', '_')}"

        def _write_local():
            with open(local_path, "wb") as f:
                f.write(screenshot_bytes)

        # Offload synchronous file write to a thread to prevent blocking the async event loop
        await asyncio.to_thread(_write_local)
        logger.info(f"Screenshot saved locally: {local_path}")
        return f"file://{local_path}"

    # Upload to Cloud Storage
    def _upload_to_gcs():
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(screenshot_bytes, content_type="image/png")

    # Offload synchronous GCS upload to a thread to prevent blocking the async event loop
    await asyncio.to_thread(_upload_to_gcs)

    url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    logger.info(f"Screenshot uploaded: {url}")
    return url
