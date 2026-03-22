## 2024-05-24 - Parallelize independent synchronous operations
**Learning:** Found multiple synchronous `.get()` queries occurring sequentially within an asynchronous route (`/api/stats`), blocking the thread and increasing latency unnecessarily.
**Action:** Use `asyncio.to_thread` and `asyncio.gather` to run independent blocking calls concurrently.
