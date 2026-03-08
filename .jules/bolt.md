## 2024-05-20 - Fast API blocking endpoints
**Learning:** Synchronous Firestore queries (e.g., `db.collection(...).get()`) inside FastAPI `async def` endpoints block the main event loop and significantly increase response latency if executed sequentially.
**Action:** When working in FastAPI `async def` endpoints, offload synchronous I/O operations using `asyncio.to_thread` and execute independent operations concurrently using `asyncio.gather`.
