## 2024-05-18 - Parallelized Firestore queries in async route
**Learning:** In FastAPI async endpoints, executing synchronous Firestore queries (like `.count().get()`) sequentially blocks the event loop.
**Action:** Use `asyncio.to_thread` combined with `asyncio.gather` to execute these synchronous operations concurrently and unblock the event loop, thereby changing the latency from the sum of all queries to the max of the queries.
