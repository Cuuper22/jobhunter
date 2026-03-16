## 2024-05-15 - Asyncio gather for synchronous I/O
**Learning:** Found sequential blocking Firestore `.get()` queries in an `async def` handler.
**Action:** Use `asyncio.to_thread` and `asyncio.gather` to execute synchronous I/O concurrently without blocking the event loop.
