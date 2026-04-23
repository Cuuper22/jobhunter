## 2024-04-23 - Prevent Event Loop Blocking in FastAPI Routes
**Learning:** The `google-cloud-firestore` Python client's synchronous methods (like `.get()`) block the asyncio event loop when used directly inside `async def` FastAPI routes, severely limiting concurrent request throughput. The client uses thread-safe gRPC channels, making it safe to parallelize.
**Action:** Use `await asyncio.to_thread()` to offload synchronous Firestore I/O operations to worker threads in async routes, preserving the event loop's responsiveness.
