
## 2025-03-01 - [Firestore N+1 Query in Scraper]
**Learning:** Found an N+1 performance bottleneck specific to how the scraper deduplicates and saves jobs to Firestore. The scraper iterated sequentially over DataFrame rows, making individual `.get()` queries and individual `.set()` writes per job. This caused immense network latency overhead during large scrape cycles.
**Action:** Replaced sequential operations with batch writes (`db.batch().commit()`) limited to Firestore's 500 max writes, and optimized deduplication by bulk querying chunks of 30 URLs using Firestore's `in` filter operator (`filter=FieldFilter("url", "in", chunk)`).
