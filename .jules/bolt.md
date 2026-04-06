## 2025-02-23 - Batch Firestore Insertions & Intra-Batch Deduplication
**Learning:** Firestore `in` queries (limit 30) and batch writes (limit 500) significantly improve N+1 query loops. However, when batch-querying "existing items" and then processing a new list, if the new list itself contains duplicates, they bypass the DB existence check and get inserted multiple times.
**Action:** Always maintain a local state (e.g., `existing_urls.add(url)`) within the processing loop of batch jobs to prevent intra-batch duplication when multiple identical items arrive in the same payload.
