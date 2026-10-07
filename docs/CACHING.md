# Caching

Temporary cache: bounded in-process TTL/LRU for short-lived results.

Persistent cache: bounded SQLite cache at `data/cache/persistent/` with TTL cleanup and importance-aware eviction.

Caches are not permanent memory and must never store secrets, credentials, tokens or authentication cookies.
