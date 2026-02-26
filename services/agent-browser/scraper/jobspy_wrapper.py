"""Wrapper around python-jobspy for multi-board job scraping."""

import logging
from datetime import datetime

from jobspy import scrape_jobs

from shared.firestore_client import job_exists, save_job, log
from shared.models import Job, JobSource, LogLevel
from agent_browser.scraper.config import SearchConfig, DEFAULT_SEARCHES

logger = logging.getLogger(__name__)

# Map JobSpy site names to our enum
SOURCE_MAP = {
    "indeed": JobSource.INDEED,
    "linkedin": JobSource.LINKEDIN,
    "glassdoor": JobSource.GLASSDOOR,
    "google": JobSource.GOOGLE,
    "zip_recruiter": JobSource.ZIP_RECRUITER,
}


def run_search(config: SearchConfig) -> list[Job]:
    """Run a single JobSpy search and return new (non-duplicate) jobs."""
    logger.info(f"Scraping: '{config.search_term}' in '{config.location or 'Remote'}'")

    try:
        df = scrape_jobs(
            site_name=config.site_names,
            search_term=config.search_term,
            location=config.location if config.location else None,
            distance=config.distance,
            results_wanted=config.results_wanted,
            hours_old=config.hours_old,
            is_remote=config.is_remote,
            country_indeed=config.country_indeed,
            linkedin_fetch_description=config.linkedin_fetch_description,
            proxy=config.proxy,
        )
    except Exception as e:
        logger.error(f"JobSpy scrape failed: {e}")
        log(f"Scrape failed for '{config.search_term}': {e}", level=LogLevel.ERROR)
        return []

    if df is None or df.empty:
        logger.info("No results returned")
        return []

    new_jobs = []
    for _, row in df.iterrows():
        url = str(row.get("job_url", ""))
        if not url or job_exists(url):
            continue

        job = Job(
            title=str(row.get("title", "Unknown")),
            company=str(row.get("company", "Unknown")),
            location=str(row.get("location", "")),
            description=str(row.get("description", "")),
            url=url,
            source=SOURCE_MAP.get(str(row.get("site", "")), JobSource.INDEED),
            salary_min=_safe_float(row.get("min_amount")),
            salary_max=_safe_float(row.get("max_amount")),
            date_posted=_safe_datetime(row.get("date_posted")),
            is_remote=bool(row.get("is_remote", False)),
        )

        job_id = save_job(job)
        job.id = job_id
        new_jobs.append(job)

    logger.info(f"Found {len(new_jobs)} new jobs (filtered {len(df) - len(new_jobs)} duplicates)")
    log(
        f"Scraped '{config.search_term}': {len(new_jobs)} new, {len(df)} total",
        level=LogLevel.SUCCESS,
        metadata={"search_term": config.search_term, "location": config.location},
    )
    return new_jobs


def run_all_searches(searches: list[SearchConfig] | None = None) -> list[Job]:
    """Run all configured searches and return all new jobs."""
    searches = searches or DEFAULT_SEARCHES
    all_jobs = []
    for search in searches:
        jobs = run_search(search)
        all_jobs.extend(jobs)
    log(
        f"Scrape cycle complete: {len(all_jobs)} new jobs across {len(searches)} searches",
        level=LogLevel.SUCCESS,
    )
    return all_jobs


def _safe_float(val) -> float | None:
    import math
    try:
        if val is None:
            return None
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return None


def _safe_datetime(val) -> datetime | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(str(val))
    except (ValueError, TypeError):
        return None
