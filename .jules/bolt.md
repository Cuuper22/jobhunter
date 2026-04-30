## 2024-06-25 - FastAPI blocking with Firestore
**Learning:** Even though Firestore requests are mostly IO bound, calling `.get()` synchronously in a `def async` FastAPI endpoint blocks the asyncio event loop.
**Action:** Always wrap synchronous database/IO calls in `asyncio.to_thread` and concurrently await them using `asyncio.gather` inside `async def` endpoints.
