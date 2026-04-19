
## 2024-05-18 - Firestore N+1 Query & Write Bottlenecks
**Learning:** Using `db.collection().where().limit(1).get()` inside a loop for deduplication and individual `db.collection().document().set()` calls create massive network overhead and bottleneck scraping pipelines.
**Action:** Always prefer chunked `in` queries (up to 30 items) to check for existence, and batched writes (up to 500 items) to save new entities. Deduplicating the ID list beforehand (`list(set(urls))`) prevents wasted queries, and using an `existing_urls.add()` within the local loop ensures intra-batch duplicates are dropped efficiently.
