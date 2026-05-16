## 2024-05-19 - Parallelize Synchronous Database Calls in FastAPI
**Learning:** Google Cloud Firestore Python SDK uses thread-safe gRPC channels. This means synchronous calls like `.get()` or `.count().get()` can be safely offloaded to threads. When an endpoint makes multiple independent synchronous requests, executing them sequentially blocks the asyncio event loop and multiplies latency.
**Action:** Use `asyncio.to_thread` coupled with `asyncio.gather` to execute independent synchronous database queries concurrently in a FastAPI route.
