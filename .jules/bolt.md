## 2024-05-18 - Avoid Blocking Event Loop in FastAPI
**Learning:** Synchronous network calls (like standard Google Cloud Firestore `.get()` and `.update()`) inside an `async def` FastAPI route will block the entire event loop, causing severe concurrency bottlenecks.
**Action:** Always wrap synchronous SDK calls in `await asyncio.to_thread(...)` when used inside asynchronous web server routes, or use an async-native SDK if available.
