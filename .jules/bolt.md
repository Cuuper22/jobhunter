## $(date +%Y-%m-%d) - [Optimize Scraper DB Operations]
**Learning:** Firestore has limits on `in` queries (30 elements max) and batched operations (500 per batch). Additionally, fetching full documents just to check existence is inefficient.
**Action:** When performing bulk existence checks, chunk requests to respect the `in` limit and use `.select(["url"])` to minimize bandwidth. Always use `db.batch()` for bulk saves, also chunking as needed.
