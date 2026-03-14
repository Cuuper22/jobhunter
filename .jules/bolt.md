## 2024-05-28 - Avoid blocking the event loop with synchronous Firestore operations

**Learning:** When using the `google-cloud-firestore` synchronous client (which returns `.get()` directly rather than awaitables) within an asynchronous framework like FastAPI, performing sequential database operations directly inside the `async def` handler will block the event loop, causing poor concurrency and increased latency. In `api-gateway`'s `/api/stats` endpoint, four sequential `.count().get()` calls were blocking the main thread.

**Action:** Whenever multiple independent synchronous IO operations (like Firestore queries or external API calls) need to be made within an async function, wrap them in `asyncio.to_thread` and execute them concurrently using `asyncio.gather()`. This offloads the blocking operations to worker threads, freeing up the event loop and potentially running the operations in parallel.
