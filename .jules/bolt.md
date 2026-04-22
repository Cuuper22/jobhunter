
## 2024-05-27 - Backend N+1 Query Optimization
**Learning:** Found an N+1 query pattern during job scraping in `jobspy_wrapper.py` where each scraped job sequentially checked Firestore for existence and sequentially saved itself. Firestore has specific limitations: `in` queries are limited to 30 elements, and batched writes are limited to 500 operations.
**Action:** Implemented `get_existing_job_urls` (chunked by 30) and `save_jobs_batch` (chunked by 500) to drastically reduce database round trips while respecting Firestore limits. Added a local `existing_urls.add(url)` within the loop to prevent saving duplicates when a scraped batch contains identical URLs.
