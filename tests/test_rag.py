import tempfile
from pathlib import Path
from jarvis_app.rag.manager import RAGManager
from jarvis_app.memory.sqlite import MemoryStore

def test_ingest_and_search():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); f=root/'doc.txt'; f.write_text('JARVIS uses a local Qwen model and SQLite memory.',encoding='utf-8')
        r=RAGManager(MemoryStore(root/'db.sqlite3')); out=r.ingest(f); assert out['chunks']>=1; assert r.search('JARVIS')
