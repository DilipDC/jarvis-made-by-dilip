# RAG

The current core uses SQLite FTS5 for lightweight keyword retrieval and supports TXT/PDF/DOCX/CSV ingestion. Chunk metadata and hashes are persisted. Semantic vector retrieval is an optional extension because embedding models add RAM cost on low-memory hardware.
