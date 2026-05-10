## 2024-05-10 - Parallelize Firestore Queries
**Learning:** Consecutive Firestore `.count().get()` aggregations in FastAPI async routes block the event loop and increase latency when run sequentially.
**Action:** Wrap synchronous I/O operations inside `asyncio.to_thread()` and run them concurrently with `asyncio.gather` to improve performance and prevent event loop blocking.
