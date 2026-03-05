
## 2024-05-18 - [Offload Sync I/O in Async Contexts]
**Learning:** Found an instance in `capture_screenshot` where synchronous file writes and Google Cloud Storage uploads were being executed directly inside an `async def` function, which blocks the asyncio event loop and slows down concurrent task execution in the API.
**Action:** Use `asyncio.to_thread` to wrap synchronous I/O operations (like local `with open` and GCS `blob.upload_from_string`) inside async contexts to maintain responsiveness.
