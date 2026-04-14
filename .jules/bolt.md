## 2024-04-14 - Offload synchronous Firestore queries to thread pool
**Learning:** In the FastAPI backend (`services/api-gateway/routers/jobs.py`), synchronous Firestore `get()` queries were being executed directly inside asynchronous endpoints (`async def`). This blocks the asyncio event loop and prevents the server from handling concurrent requests efficiently.
**Action:** Always wrap synchronous database I/O or network requests inside `async def` FastAPI routes with `await asyncio.to_thread(...)` to offload them to a thread pool and maintain high concurrency.
