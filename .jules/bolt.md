## 2025-02-12 - Parallelized Sync Database Aggregation Queries
**Learning:** Found sequential `.count().get()` calls inside a FastAPI `async def` route that were blocking the asyncio event loop.
**Action:** When working with synchronous Firestore operations inside FastAPI `async def` routes, wrap each independent call with `asyncio.to_thread` and use `asyncio.gather` to execute them concurrently. This prevents blocking the event loop and speeds up the endpoint response by parallelizing I/O.
