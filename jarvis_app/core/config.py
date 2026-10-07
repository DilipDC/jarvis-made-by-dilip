from __future__ import annotations
import json, os
from dataclasses import dataclass, field
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; DATA_DIR=ROOT/'data'; CONFIG_DIR=ROOT/'config'
@dataclass(slots=True)
class Settings:
    general_model:str='qwen3:0.6b'; coding_model:str='qwen2.5-coder:1.5b'; ollama_url:str='http://127.0.0.1:11434'; low_ram_mode:bool=True
    cache_max_entries:int=256; cache_max_bytes:int=8*1024*1024; trusted_paths:list[str]=field(default_factory=list); python_timeout:int=120; terminal_timeout:int=30; web_timeout:int=12; browser_enabled:bool=True; openai_enabled:bool=False; openai_model:str='gpt-5.6-luna'
    profile:dict=field(default_factory=dict)
    @classmethod
    def load(cls)->'Settings':
        s=cls(); s.general_model=os.getenv('GENERAL_MODEL',s.general_model); s.coding_model=os.getenv('CODING_MODEL',s.coding_model); s.ollama_url=os.getenv('OLLAMA_URL',s.ollama_url).rstrip('/'); s.low_ram_mode=os.getenv('LOW_RAM_MODE','true').lower() in {'1','true','yes','on'}; s.cache_max_entries=int(os.getenv('CACHE_MAX_ENTRIES',s.cache_max_entries)); s.cache_max_bytes=int(os.getenv('CACHE_MAX_BYTES',s.cache_max_bytes)); s.python_timeout=int(os.getenv('PYTHON_TIMEOUT',s.python_timeout)); s.terminal_timeout=int(os.getenv('TERMINAL_TIMEOUT',s.terminal_timeout)); s.web_timeout=int(os.getenv('WEB_TIMEOUT',s.web_timeout)); raw=os.getenv('TRUSTED_PATHS',''); s.trusted_paths=[str(Path(x).expanduser().resolve()) for x in raw.split(os.pathsep) if x.strip()] or [str(ROOT/'scripts'),str(ROOT/'projects'),str(ROOT)]
        s.openai_enabled=os.getenv('OPENAI_ENABLED','false').lower() in {'1','true','yes','on'}; s.openai_model=os.getenv('OPENAI_MODEL',s.openai_model); s.profile=load_profile(); return s
def load_profile()->dict:
    p=CONFIG_DIR/'profile.json'
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return {'name':'User','assistant_name':'JARVIS','welcome_enabled':True,'welcome_style':'brief','interests':[],'preferred_language':'English'}
