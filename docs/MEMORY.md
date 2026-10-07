# Memory

Long-term memories use SQLite. The temporary cache uses TTL/LRU/size bounds. Relevant memories are injected into model context only when available instead of sending full history.
