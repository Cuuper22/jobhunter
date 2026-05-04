## 2024-05-24 - Parallelize concurrent sync database aggregations
**Learning:** Independent synchronous database queries within FastAPI async routes block the event loop and incur sequential network latency penalties.
**Action:** Always wrap independent synchronous queries in `asyncio.to_thread` and execute them concurrently with `asyncio.gather` inside `async def` routes.
