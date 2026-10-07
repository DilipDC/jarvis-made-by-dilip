from jarvis_app.cache.cache import CacheManager
from jarvis_app.models.router import ModelRouter
from jarvis_app.agents.builtins import build_agent_manager

def test_cache_round_trip(tmp_path):
    c=CacheManager(root=tmp_path/"cache",temp_max_entries=4,temp_max_bytes=1024); k=c.key("test","one"); c.set(k,{"ok":True},ttl=30,source="test"); assert c.get(k)=={"ok":True}

def test_router():
    r=ModelRouter("Qwen/Qwen3-0.6B","Qwen/Qwen2.5-Coder-1.5B"); assert r.route("debug this Python code")=="Qwen/Qwen2.5-Coder-1.5B"; assert r.route("what time is it")=="Qwen/Qwen3-0.6B"

def test_agent_budget():
    m=build_agent_manager("general","coder",4,2,2); assert m.snapshot()["count"]==10; assert m.select("coding","fix this repo")=="CodingAgent"
