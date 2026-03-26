## 2024-05-24 - Parallelizing Firestore Queries in FastAPI
**Learning:** Synchronous Firestore queries (e.g., `.get()`) block the FastAPI event loop when used directly in `async def` routes. The `google-cloud-firestore` Python client uses gRPC channels which are thread-safe, making it safe to parallelize synchronous database calls across multiple threads.
**Action:** Use `asyncio.to_thread` to offload synchronous Firestore queries and use `asyncio.gather` to run independent queries concurrently.
