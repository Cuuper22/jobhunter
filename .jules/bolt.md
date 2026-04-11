
## 2024-05-24 - Async IO Thread Offloading
**Learning:** In backend FastAPI microservices using Google Cloud Firestore via synchronous Python client (`google-cloud-firestore`), synchronous database calls directly inside asynchronous endpoints (e.g., `async def`) block the event loop, causing severe latency and throughput issues.
**Action:** Always offload blocking synchronous I/O operations (such as `.get()`, `.update()`, or synchronous logger calls) to a thread pool using `await asyncio.to_thread(func, *args, **kwargs)` in FastAPI.
