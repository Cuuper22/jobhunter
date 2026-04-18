## 2024-05-30 - Prevent FastAPI Event Loop Blocking from Firestore Sync Calls
**Learning:** The Google Cloud Firestore python client is primarily synchronous. When FastAPI routes call `db.collection(...).get()`, it blocks the asyncio event loop, causing requests to queue up and increasing latency under load.
**Action:** Always wrap synchronous I/O, especially Firestore `.get()`, `.update()`, and `.set()` calls in `asyncio.to_thread` when inside asynchronous FastAPI handlers.
