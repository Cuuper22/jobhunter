## 2024-05-09 - Parallelizing synchronous Firestore queries in FastAPI
**Learning:** Multiple independent synchronous database queries within FastAPI async routes (like consecutive Firestore `.count().get()` aggregations) run sequentially, multiplying network latency and blocking the event loop.
**Action:** Wrap independent I/O-bound synchronous calls in `asyncio.to_thread` and run them concurrently using `asyncio.gather` to reduce latency and prevent blocking the asyncio event loop.
