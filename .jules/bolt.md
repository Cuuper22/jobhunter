## 2024-04-03 - Parallelize synchronous Firestore operations
**Learning:** The Google Cloud Firestore python client's synchronous methods (like `.get()`) block the main thread and event loop.
**Action:** Use `asyncio.to_thread` alongside `asyncio.gather` to execute these synchronous database calls concurrently within asynchronous FastAPI endpoints.
