## 2024-05-03 - [Parallelizing synchronous Firestore calls in async FastAPI routes]
**Learning:** Sequential synchronous Firestore queries (like `.count().get()`) inside FastAPI `async def` routes block the event loop and compound request latency.
**Action:** Wrap independent synchronous database calls in `asyncio.to_thread` and execute them concurrently using `asyncio.gather` within async routes to improve throughput and response times.
