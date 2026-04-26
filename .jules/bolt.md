## 2024-05-19 - Parallelizing Firestore Queries
**Learning:** Found multiple independent synchronous database queries within FastAPI async routes (`/api/stats` endpoint) that block the event loop and increase latency linearly with each `.count().get()` call.
**Action:** Always wrap independent synchronous queries in `asyncio.to_thread` and run them concurrently with `asyncio.gather` inside FastAPI asynchronous endpoints to avoid blocking the event loop.
