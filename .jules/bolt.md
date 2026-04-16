## 2024-05-24 - Async IO Offloading for Firestore Queries
**Learning:** The 'google-cloud-firestore' Python client performs synchronous network I/O during operations like '.get()'. In asynchronous frameworks like FastAPI, awaiting or directly calling these methods inside 'async def' route handlers blocks the entire event loop, preventing the server from handling concurrent requests efficiently.
**Action:** Always wrap synchronous Firestore operations (like 'query.get()') with 'asyncio.to_thread' in FastAPI endpoints.
