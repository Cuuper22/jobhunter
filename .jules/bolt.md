## 2024-04-07 - Initializing Bolt Journal
**Learning:** Initializing journal for Bolt optimization tasks.
**Action:** Ready to profile and optimize.
## 2024-04-07 - Profiling backend operations
**Learning:** Found sequential Firestore `.count().get()` calls in `/api/stats` in `services/api-gateway/main.py`.
**Action:** Can use `asyncio.gather` with `asyncio.to_thread` to parallelize these synchronous operations and improve endpoint latency.
