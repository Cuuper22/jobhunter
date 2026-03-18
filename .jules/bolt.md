## 2024-05-18 - Offload Synchronous Operations in FastApi Async Routes
**Learning:** Synchronous Firestore operations (like `.get()`, `.update()`, etc.) run inside an `async def` route handler block the main event loop, leading to severe performance bottlenecks under concurrent load. The `google-cloud-firestore` Python client gRPC channels are thread-safe.
**Action:** Use `await asyncio.to_thread(sync_func, *args, **kwargs)` to offload these blocking I/O calls to a separate thread, freeing the main loop to handle other requests.
