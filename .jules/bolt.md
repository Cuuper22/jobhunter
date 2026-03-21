## 2024-05-24 - [Parallelize synchronous Firestore queries in FastAPI async routes]
**Learning:** Sequential synchronous Firestore queries (`.get()`) in an async route block the event loop and increase latency linearly with the number of queries. The `google-cloud-firestore` Python client uses gRPC channels which are thread-safe.
**Action:** Use `asyncio.to_thread` to offload synchronous database calls (like `.get()`) to separate threads, and run them concurrently using `asyncio.gather` within FastAPI asynchronous routes.
