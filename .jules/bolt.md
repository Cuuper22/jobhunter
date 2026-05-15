## 2024-05-16 - Firestore N+1 Query Bottleneck in Scraping
**Learning:** The scraper used N+1 sequential Firestore queries (`job_exists` and `save_job`) inside a loop over the job dataframe. Because network latency dominates database calls, this significantly bottlenecked processing of bulk scraped items.
**Action:** When working with scraped jobs or bulk records, always use chunked batched Firestore reads (`in` queries limited to 30 items) and writes (`batch()` limited to 500 operations). Also implement local intra-batch deduplication before persisting.
