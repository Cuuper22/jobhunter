import asyncio
import time
from unittest.mock import MagicMock

class MockCount:
    def get(self):
        time.sleep(0.1) # Simulate network delay
        m = MagicMock()
        m.value = 42
        return [[m]]

class MockCollection:
    def count(self):
        return MockCount()
    def where(self, *args, **kwargs):
        return self

class MockDB:
    def collection(self, name):
        return MockCollection()

db = MockDB()

async def original_stats():
    start = time.time()
    jobs_count = db.collection("jobs").count().get()[0][0].value
    apps_count = db.collection("applications").count().get()[0][0].value
    pending_count = db.collection("applications").where("status", "==", "pending_approval").count().get()[0][0].value
    submitted_count = db.collection("applications").where("status", "==", "submitted").count().get()[0][0].value
    end = time.time()
    print(f"Original took: {end - start:.3f}s")
    return {"jobs": jobs_count, "apps": apps_count, "pending": pending_count, "submitted": submitted_count}

async def optimized_stats():
    start = time.time()

    def get_jobs_count():
        return db.collection("jobs").count().get()[0][0].value

    def get_apps_count():
        return db.collection("applications").count().get()[0][0].value

    def get_pending_count():
        return db.collection("applications").where("status", "==", "pending_approval").count().get()[0][0].value

    def get_submitted_count():
        return db.collection("applications").where("status", "==", "submitted").count().get()[0][0].value

    results = await asyncio.gather(
        asyncio.to_thread(get_jobs_count),
        asyncio.to_thread(get_apps_count),
        asyncio.to_thread(get_pending_count),
        asyncio.to_thread(get_submitted_count),
    )
    end = time.time()
    print(f"Optimized took: {end - start:.3f}s")
    return {"jobs": results[0], "apps": results[1], "pending": results[2], "submitted": results[3]}

async def run():
    print(await original_stats())
    print(await optimized_stats())

asyncio.run(run())
