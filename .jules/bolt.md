## 2024-05-24 - Firestore Synchronous Operations in Async Contexts
**Learning:** Found synchronous Firestore operations (`.get()`) running sequentially in an `async` FastAPI route (`/api/stats`), blocking the event loop and reducing concurrency.
**Action:** Use `asyncio.to_thread` for synchronous IO operations and combine independent calls with `asyncio.gather` to execute them concurrently, or use async firestore client.
