1. **Add batched operations in `services/shared/firestore_client.py`**:
   - Add `get_existing_job_urls(urls: list[str]) -> set[str]` using `in` queries (chunked to 30 elements).
   - Add `save_jobs_batch(jobs: list[Job]) -> list[str]` using `db.batch()` (chunked to 500 operations).
2. **Optimize `services/agent-browser/scraper/jobspy_wrapper.py`**:
   - In `run_search()`, extract all URLs from the dataframe and fetch their existence in bulk using `get_existing_job_urls`.
   - Iterate through the dataframe to build a list of `Job` objects that don't exist in the database (ensuring intra-batch local deduplication using `existing_urls.add(url)`).
   - Bulk save the new jobs using `save_jobs_batch`.
3. **Verify the optimization**:
   - Write a standalone test script to ensure `get_existing_job_urls` and `save_jobs_batch` compile and don't have syntax errors.
   - Run the existing tests via `PYTHONPATH=services python3 -m unittest discover services`.
4. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
5. **Submit the PR**:
   - Create a PR titled `⚡ Bolt: [performance improvement]` solving the N+1 query problem.
