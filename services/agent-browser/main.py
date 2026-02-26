"""Agent-Browser service — Cloud Run entry point.

Handles two types of requests:
1. POST /scrape — Run a scrape cycle across all job boards
2. POST /process — Score a job, generate cover letter, and create application
3. POST /apply — Pre-fill application form for an approved application
"""

import asyncio
import logging
import os
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared.firestore_client import (
    get_job, save_application, update_application_status, update_job_score, log,
)
from shared.models import Application, ApplicationStatus, LogLevel

from agent_browser.scraper.jobspy_wrapper import run_all_searches
from agent_browser.scraper.config import DEFAULT_SEARCHES
from agent_browser.ai.cover_letter import generate_cover_letter
from agent_browser.ai.job_scorer import score_job
from agent_browser.ai.outreach_email import generate_outreach_email
from agent_browser.context.loader import get_user_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="JobHunter Agent-Browser")

# Default form data for applications (loaded from env/config)
DEFAULT_FORM_DATA = {
    "first_name": os.getenv("APPLICANT_FIRST_NAME", "Yousef"),
    "last_name": os.getenv("APPLICANT_LAST_NAME", "Anas"),
    "email": os.getenv("APPLICANT_EMAIL", "APPLICANT_EMAIL_REDACTED"),
    "phone": os.getenv("APPLICANT_PHONE", "PHONE_REDACTED"),
    "resume_path": os.getenv("RESUME_PATH", "/app/context/resume.pdf"),
}

# --- Scraping ---


class ScrapeResponse(BaseModel):
    new_jobs: int
    message: str


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_jobs():
    """Run a full scrape cycle across all configured searches."""
    log("Starting scrape cycle", level=LogLevel.INFO)
    try:
        jobs = run_all_searches(DEFAULT_SEARCHES)
        return ScrapeResponse(
            new_jobs=len(jobs),
            message=f"Scrape complete: {len(jobs)} new jobs found",
        )
    except Exception as e:
        log(f"Scrape cycle failed: {e}", level=LogLevel.ERROR)
        raise HTTPException(status_code=500, detail=str(e))


# --- Batch processing (scrape + score + cover letter for all unscored jobs) ---


class BatchResponse(BaseModel):
    new_jobs: int
    processed: int
    applications_created: int
    message: str


@app.post("/scrape-and-process", response_model=BatchResponse)
async def scrape_and_process(min_score: int = 40):
    """Full automated cycle: scrape new jobs, score them, generate cover letters.

    Called by Cloud Scheduler every few hours. Produces pending_approval applications
    for jobs that score above min_score.
    """
    from shared.firestore_client import db

    log("Starting automated scrape-and-process cycle", level=LogLevel.INFO)

    # Step 1: Scrape new jobs
    try:
        new_jobs = run_all_searches(DEFAULT_SEARCHES)
    except Exception as e:
        log(f"Scrape phase failed: {e}", level=LogLevel.ERROR)
        new_jobs = []

    # Step 2: Find all unscored jobs (fit_score is None)
    unscored_docs = (
        db.collection("jobs")
        .where("fit_score", "==", None)
        .limit(50)  # process max 50 per cycle to control costs
        .get()
    )

    user_context = get_user_context()
    processed = 0
    apps_created = 0

    for doc in unscored_docs:
        data = doc.to_dict()
        job_id = doc.id

        try:
            # Score the job (returns enriched dict)
            score_result = score_job(
                data.get("title", ""),
                data.get("company", ""),
                data.get("description", ""),
                user_context,
            )
            score = score_result["score"]
            reasoning = score_result["reasoning"]
            from shared.firestore_client import update_job_score
            update_job_score(job_id, score, reasoning)
            processed += 1

            log(
                f"Scored '{data.get('title')}' at {data.get('company')}: {score}/100",
                level=LogLevel.INFO,
                job_id=job_id,
            )

            # If score is good enough, generate cover letter
            if score >= min_score:
                cover_letter = generate_cover_letter(
                    data.get("title", ""),
                    data.get("company", ""),
                    data.get("description", ""),
                    user_context,
                )

                application = Application(
                    job_id=job_id,
                    job_title=data.get("title", ""),
                    company=data.get("company", ""),
                    job_url=data.get("url", ""),
                    status=ApplicationStatus.PENDING_APPROVAL,
                    cover_letter=cover_letter,
                    form_data={**DEFAULT_FORM_DATA, "cover_letter": cover_letter},
                    fit_score=score,
                    fit_reasoning=reasoning,
                    role_summary=score_result.get("role_summary"),
                    company_summary=score_result.get("company_summary"),
                    strengths=score_result.get("strengths"),
                    gaps=score_result.get("gaps"),
                    suggestions=score_result.get("suggestions"),
                )
                app_id = save_application(application)
                apps_created += 1

                log(
                    f"Draft ready for '{data.get('title')}' at {data.get('company')} (score: {score})",
                    level=LogLevel.SUCCESS,
                    job_id=job_id,
                    application_id=app_id,
                )

        except Exception as e:
            log(f"Processing failed for job {job_id}: {e}", level=LogLevel.ERROR, job_id=job_id)

    summary = f"Cycle complete: {len(new_jobs)} new jobs scraped, {processed} scored, {apps_created} applications created"
    log(summary, level=LogLevel.SUCCESS)

    return BatchResponse(
        new_jobs=len(new_jobs),
        processed=processed,
        applications_created=apps_created,
        message=summary,
    )


# --- Processing (score + cover letter) ---


class ProcessRequest(BaseModel):
    job_id: str
    min_score: int = 40  # only generate cover letter if score >= this


class ProcessResponse(BaseModel):
    job_id: str
    score: int
    reasoning: str
    application_id: str | None = None
    cover_letter_preview: str | None = None


@app.post("/process", response_model=ProcessResponse)
async def process_job(req: ProcessRequest):
    """Score a job and optionally generate a cover letter + application draft."""
    job = get_job(req.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    user_context = get_user_context()

    # Score the job (returns enriched dict)
    score_result = score_job(job.title, job.company, job.description, user_context)
    score = score_result["score"]
    reasoning = score_result["reasoning"]
    update_job_score(req.job_id, score, reasoning)

    log(
        f"Scored '{job.title}' at {job.company}: {score}/100",
        level=LogLevel.INFO,
        job_id=req.job_id,
    )

    # If score is high enough, generate cover letter and create application
    application_id = None
    cover_letter_preview = None

    if score >= req.min_score:
        cover_letter = generate_cover_letter(
            job.title, job.company, job.description, user_context
        )
        cover_letter_preview = cover_letter[:200] + "..."

        application = Application(
            job_id=req.job_id,
            job_title=job.title,
            company=job.company,
            job_url=job.url,
            status=ApplicationStatus.PENDING_APPROVAL,
            cover_letter=cover_letter,
            form_data={**DEFAULT_FORM_DATA, "cover_letter": cover_letter},
            fit_score=score,
            fit_reasoning=reasoning,
            role_summary=score_result.get("role_summary"),
            company_summary=score_result.get("company_summary"),
            strengths=score_result.get("strengths"),
            gaps=score_result.get("gaps"),
            suggestions=score_result.get("suggestions"),
        )
        application_id = save_application(application)

        log(
            f"Draft ready for '{job.title}' at {job.company} (score: {score})",
            level=LogLevel.SUCCESS,
            job_id=req.job_id,
            application_id=application_id,
        )

    return ProcessResponse(
        job_id=req.job_id,
        score=score,
        reasoning=reasoning,
        application_id=application_id,
        cover_letter_preview=cover_letter_preview,
    )


# --- Application submission ---


class ApplyRequest(BaseModel):
    application_id: str


class ApplyResponse(BaseModel):
    success: bool
    screenshot_url: str | None = None
    error: str | None = None


@app.post("/apply", response_model=ApplyResponse)
async def apply_to_job(req: ApplyRequest):
    """Pre-fill an application form using Playwright.

    This is called AFTER the user approves an application via the dashboard.
    """
    from agent_browser.applicator.form_filler import prefill_application
    from playwright.async_api import async_playwright

    application = None
    try:
        from shared.firestore_client import get_application
        application = get_application(req.application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        if application.status != ApplicationStatus.APPROVED:
            raise HTTPException(
                status_code=400,
                detail=f"Application status is {application.status}, expected APPROVED",
            )

        update_application_status(req.application_id, ApplicationStatus.SUBMITTING)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            success, ats_type, screenshot_url = await prefill_application(
                page=page,
                job_url=application.job_url,
                form_data=application.form_data or DEFAULT_FORM_DATA,
                job_id=application.job_id,
            )

            await browser.close()

        if success:
            update_application_status(
                req.application_id,
                ApplicationStatus.SUBMITTED,
                screenshot_url=screenshot_url,
            )
            log(
                f"Application submitted for '{application.job_title}' at {application.company}",
                level=LogLevel.SUCCESS,
                application_id=req.application_id,
            )
        else:
            update_application_status(
                req.application_id,
                ApplicationStatus.DRAFT_READY,
                screenshot_url=screenshot_url,
                error_message=f"Form fill incomplete (ATS: {ats_type}). Manual review needed.",
            )
            log(
                f"Form fill incomplete for {application.company} (ATS: {ats_type})",
                level=LogLevel.WARNING,
                application_id=req.application_id,
            )

        return ApplyResponse(success=success, screenshot_url=screenshot_url)

    except HTTPException:
        raise
    except Exception as e:
        if application:
            update_application_status(
                req.application_id,
                ApplicationStatus.FAILED,
                error_message=str(e),
            )
        log(f"Apply failed: {e}", level=LogLevel.ERROR, application_id=req.application_id)
        return ApplyResponse(success=False, error=str(e))


# --- Outreach email generation ---


class OutreachRequest(BaseModel):
    job_id: str
    contact_name: str | None = None


class OutreachResponse(BaseModel):
    subject: str
    body: str


@app.post("/generate-outreach", response_model=OutreachResponse)
async def generate_outreach(req: OutreachRequest):
    """Generate a warm outreach/networking email for a job opportunity."""
    job = get_job(req.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    user_context = get_user_context()

    try:
        result = generate_outreach_email(
            job_title=job.title,
            company=job.company,
            job_description=job.description,
            user_context=user_context,
            contact_name=req.contact_name,
        )
        return OutreachResponse(subject=result["subject"], body=result["body"])
    except Exception as e:
        log(f"Outreach email generation failed: {e}", level=LogLevel.ERROR, job_id=req.job_id)
        raise HTTPException(status_code=500, detail=str(e))


# --- Health check ---


@app.get("/health")
async def health():
    return {"status": "ok", "service": "agent-browser"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
