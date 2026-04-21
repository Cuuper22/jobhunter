## YYYY-MM-DD - Prevent event loop blocking
**Learning:** Synchronous Firestore calls like `.get()` and `.update()` block the FastAPI event loop, leading to performance bottlenecks in high concurrency. The `google-cloud-firestore` gRPC channels are thread-safe, so `asyncio.to_thread` safely resolves this.
**Action:** Use `asyncio.to_thread` for all synchronous Firestore I/O inside `async def` routes.
