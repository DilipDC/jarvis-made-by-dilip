import tempfile
from pathlib import Path
from jarvis_app.memory.sqlite import MemoryStore
from jarvis_app.cache.cache import CacheManager
from jarvis_app.agent.fast_intent import classify
from jarvis_app.models.router import ModelRouter
from jarvis_app.security.permissions import PermissionManager,SAFE,CONFIRM,BLOCKED

def test_intent_and_router():
    assert classify('what is my RAM usage')=='ram'
    assert ModelRouter('qwen3:0.6b','qwen2.5-coder:1.5b').route('fix this python bug')=='qwen2.5-coder:1.5b'
def test_memory_and_cache():
    with tempfile.TemporaryDirectory() as td:
        s=MemoryStore(Path(td)/'x.sqlite3'); s.remember('project is JARVIS',importance=3); assert s.search('jarvis')[0]['content']=='project is JARVIS'
    c=CacheManager(max_entries=2,max_bytes=10000); c.set('a',1,ttl=60); assert c.get('a')==1

def test_permissions():
    p=PermissionManager(); assert p.check('open chrome').level==SAFE; assert p.check('delete file').level==CONFIRM; assert p.check('disable firewall').level==BLOCKED
