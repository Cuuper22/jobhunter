## 2024-04-24 - Parallelized Firestore `count().get()` aggregation queries in FastAPI route
**Learning:** Sequential synchronous operations (like Firestore `.count().get()`) inside an `async def` FastAPI route will block the event loop and linearly compound response latency.
**Action:** When making multiple independent synchronous database queries in FastAPI async routes, always wrap them in `asyncio.to_thread` and run them concurrently using `asyncio.gather`.
