"""Wrapper around python-jobspy for multi-board job scraping."""

import logging
from datetime import datetime

from jobspy import scrape_jobs

from shared.firestore_client import bulk_job_exists, save_jobs, log
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

    # Extract URLs for bulk check
    urls_to_check = [str(url) for url in df["job_url"].dropna().unique() if str(url)]

    # Check which ones already exist
    existing_urls = bulk_job_exists(urls_to_check) if urls_to_check else set()

    jobs_to_save = []
    for _, row in df.iterrows():
        url = str(row.get("job_url", ""))
        if not url or url in existing_urls:
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

        # Deduplicate internally within the new scrape batch
        existing_urls.add(url)
        jobs_to_save.append(job)

    if jobs_to_save:
        save_jobs(jobs_to_save)

    logger.info(f"Found {len(jobs_to_save)} new jobs (filtered {len(df) - len(jobs_to_save)} duplicates)")
    log(
        f"Scraped '{config.search_term}': {len(jobs_to_save)} new, {len(df)} total",
        level=LogLevel.SUCCESS,
        metadata={"search_term": config.search_term, "location": config.location},
    )
    return jobs_to_save


def run_all_searches(searches: list[SearchConfig] | None = None) -> list[Job]:
    """Run all configured searches and return all new jobs."""
    import time
    searches = searches or DEFAULT_SEARCHES
    all_jobs = []
    for i, search in enumerate(searches):
        if i > 0:
            # Delay between searches to avoid rate limiting (10-15s)
            delay = 10 + (i % 3) * 2
            logger.info(f"Waiting {delay}s before next search...")
            time.sleep(delay)
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
