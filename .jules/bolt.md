
## 2024-10-24 - Offloading synchronous Firestore operations
**Learning:** The Google Cloud Firestore Python SDK operates synchronously and makes network calls over gRPC. In FastAPI, using these operations (e.g., `db.collection(...).get()`) directly inside `async def` routes blocks the main event loop, significantly degrading concurrency and performance for parallel requests. The Firestore gRPC channels are thread-safe.
**Action:** Always wrap synchronous Firestore I/O (like `.get()`, `.update()`, or `.add()`) inside `await asyncio.to_thread(...)` when executed from an `async def` FastAPI route, allowing the event loop to continue processing other concurrent requests.
