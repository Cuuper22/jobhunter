## 2024-05-24 - Batched Firestore Writes in Job Scraper
**Learning:** Sequential Firestore queries and writes in loops (`job_exists` checking and `save_job`) inside `run_search` can severely bottleneck job scraping, leading to N+1 query performance problems.
**Action:** Replace sequential reads with `get_existing_job_urls` leveraging Firestore 'in' queries (chunked by 30), and batched writes via `save_jobs_batch` (chunked by 500) to minimize network roundtrips. Ensure local intra-batch deduplication to prevent duplicates.
