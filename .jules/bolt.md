## 2024-11-20 - Parallelize consecutive async I/O calls
**Learning:** Multiple independent synchronous database queries within FastAPI async routes (like consecutive Firestore `.count().get()` aggregations) block the event loop and add up latencies.
**Action:** Parallelize them by wrapping each query in `asyncio.to_thread` and running them concurrently with `asyncio.gather` to reduce overall latency and prevent event loop blocking.
