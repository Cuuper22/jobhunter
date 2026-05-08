## 2024-05-24 - Parallelize Firestore queries in async routes
**Learning:** Multiple independent synchronous database queries within FastAPI async routes (like consecutive Firestore `.count().get()` aggregations) block the event loop and accumulate latency.
**Action:** Parallelize them by wrapping them in `asyncio.to_thread` and running them concurrently with `asyncio.gather` to reduce latency and prevent event loop blocking.
