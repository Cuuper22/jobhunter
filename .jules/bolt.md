## 2026-04-04 - [Firestore Batching in Scraper]
**Learning:** Sequential Firestore calls (N+1 queries) inside the scraper loop caused significant network overhead. By using the 'in' operator to chunk URLs for existence checks (up to 30 items) and batched writes (up to 500 operations) we drastically reduce latency.
**Action:** Always prefer batched operations for bulk data ingestion or checks.
