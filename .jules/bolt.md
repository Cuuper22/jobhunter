## 2024-05-05 - Optimize Firestore Scrape Inserts
**Learning:** Using sequential Firestore queries (`.get()`) in a loop for checking job existence creates a severe N+1 bottleneck during scraping.
**Action:** Use chunked Firestore `in` queries (max 30) for existence checks and `batch()` for writes (max 500) to minimize network roundtrips.
