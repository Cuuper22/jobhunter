## 2024-11-20 - Concurrent Firestore Aggregations
**Learning:** Sequential synchronous operations (`.count().get()`) within `async def` routes block the asyncio event loop, causing unnecessary request latency and degraded concurrency.
**Action:** Always wrap synchronous database/API calls within `asyncio.to_thread` and use `asyncio.gather` when they can run concurrently, especially for independent database queries like multiple dashboard metric aggregations.
