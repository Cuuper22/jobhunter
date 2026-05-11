## 2025-02-14 - Batch Firestore Operations in Web Scraping Loops
**Learning:** Sequential Firestore calls (N+1 queries) inside web scraping loops cause severe latency issues and potential blocking due to network trips per row.
**Action:** Always batch Firestore existence checks (using `in` queries with a 30-element chunk limit) and document creation (using batch writes with a 500-operation chunk limit) rather than calling them individually in a loop.
