## 2024-03-20 - Non-blocking Firestore get() operations
**Learning:** Found a performance bottleneck specific to this architecture. Synchronous Firestore `.get()` operations inside FastAPI asynchronous routes block the single-threaded event loop. This leads to reduced concurrency and slower response times.
**Action:** Always offload synchronous Firestore `get()` operations in `async def` routes to a background thread using `asyncio.to_thread()`.
