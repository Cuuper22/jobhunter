## 2026-03-24 - Parallelizing synchronous Firestore queries with asyncio
**Learning:** The `google-cloud-firestore` Python client uses gRPC channels which are thread-safe. This makes it safe to parallelize synchronous database calls (like `.get()`) across multiple threads using `asyncio.to_thread` within FastAPI asynchronous routes, achieving significant speedup when executing multiple independent queries.
**Action:** Use `asyncio.gather` with `asyncio.to_thread` to execute independent Firestore queries concurrently in FastAPI endpoints, such as the stats dashboard endpoint.
