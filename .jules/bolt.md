
## 2024-05-02 - Parallelize Synchronous Database Queries in Async Routes
**Learning:** Using synchronous I/O operations (like Firestore `.count().get()`) inside an `async def` route (like a FastAPI endpoint) blocks the asyncio event loop.
**Action:** Always wrap synchronous database queries inside `asyncio.to_thread` and use `asyncio.gather` to execute them concurrently, maximizing performance and keeping the event loop unblocked.
