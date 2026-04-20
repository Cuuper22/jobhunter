## 2024-04-20 - [Batching Firestore Operations in Scraper]
**Learning:** Checking existence and saving records individually in a loop (N+1 problem) against Firestore causes significant performance degradation during scraping tasks. Firestore limits `in` queries to 30 items and batched writes to 500 items.
**Action:** Always use batched operations (`db.batch()`) and chunked `in` queries when processing lists of items in Firestore to optimize network roundtrips and execution speed.
