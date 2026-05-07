## 2024-03-24 - Parallelizing Firestore Aggregation Queries
**Learning:** Multiple independent synchronous database queries within FastAPI async routes (like consecutive Firestore `.count().get()` aggregations) block the event loop and add up sequentially, causing increased latency.
**Action:** When performing multiple independent Firestore aggregations in async routes, wrap them in `asyncio.to_thread` and run them concurrently using `asyncio.gather` to reduce latency.
