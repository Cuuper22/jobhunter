
## 2024-05-17 - Parallelize Synchronous Database Queries in Async Routes
**Learning:** Multiple independent synchronous database queries within FastAPI async routes (like consecutive Firestore `.count().get()` aggregations) run sequentially and block the event loop, causing latency to sum up across queries.
**Action:** Always parallelize such independent synchronous operations by wrapping them in `asyncio.to_thread` and running them concurrently with `asyncio.gather` to reduce overall request latency and prevent event loop blocking.
