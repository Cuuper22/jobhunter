
## 2024-05-28 - [FastAPI Blocking Sync Calls in async def]
**Learning:** Found that synchronous Firestore queries (`.get()`) were being executed directly inside FastAPI `async def` endpoints (`/api/stats` and `/api/logs`). Because they are synchronous blocking calls, this completely blocks the main event loop, severely degrading service concurrency.
**Action:** Always wrap synchronous blocking calls (like DB queries, file I/O) in `asyncio.to_thread` when inside an `async def` route. Use `asyncio.gather` when multiple independent synchronous queries can be fetched concurrently.
