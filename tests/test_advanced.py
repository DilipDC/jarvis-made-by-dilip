import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from jarvis_app.events.bus import EventBus
from jarvis_app.memory.sqlite import MemoryStore
from jarvis_app.scheduler.scheduler import Scheduler
from jarvis_app.rag.manager import RAGManager
from jarvis_app.security.permissions import PermissionManager, CONFIRM
from jarvis_app.core.app import app

def test_scheduler_persists_and_emits():
    with tempfile.TemporaryDirectory() as td:
        store=MemoryStore(Path(td)/'db.sqlite3'); events=EventBus(); seen=[]; events.on('scheduler.add',lambda e: seen.append(e))
        scheduler=Scheduler(store,events); item=scheduler.add(3600,'remind me'); assert item['status']=='SCHEDULED'; assert seen
        scheduler.stop(); assert store.load_scheduled()[0]['id']==item['id']

def test_rag_reingest_does_not_duplicate_old_chunks():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); f=root/'a.txt'; f.write_text('alpha beta',encoding='utf-8'); r=RAGManager(MemoryStore(root/'db.sqlite3')); r.ingest(f); f.write_text('gamma delta',encoding='utf-8'); r.ingest(f)
        assert not r.search('alpha'); assert r.search('gamma')

def test_http_surface_websocket_and_stream():
    with TestClient(app) as client:
        assert client.get('/').status_code==200
        assert client.get('/api/status').status_code==200
        assert client.get('/api/doctor').status_code==200
        stream=client.get('/api/chat/stream',params={'text':'what is my RAM usage'})
        assert stream.status_code==200 and 'RAM' in stream.text
        with client.websocket_connect('/api/events') as ws:
            first=ws.receive_json(); assert first['event']=='connected'

def test_side_effects_require_confirmation():
    p=PermissionManager(); assert p.check('run terminal','echo hello').level==CONFIRM
