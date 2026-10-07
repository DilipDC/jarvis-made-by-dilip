from __future__ import annotations
import json,os
from dataclasses import dataclass,field
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; DATA_DIR=ROOT/"data"; CONFIG_DIR=ROOT/"config"
@dataclass(slots=True)
class Settings:
    general_model:str="Qwen/Qwen3-0.6B"; coding_model:str="Qwen/Qwen2.5-Coder-1.5B"; model_backend:str="airllm"; ollama_url:str="http://127.0.0.1:11434"
    ollama_general_model:str="qwen3:0.6b"; ollama_coding_model:str="qwen2.5-coder:1.5b"; low_ram_mode:bool=True
    ram_soft_limit_gb:float=3.5; ram_critical_limit_gb:float=3.85; max_context_tokens:int=768; max_new_tokens:int=192
    max_subagents:int=4; max_parallel_agents:int=2; max_agent_depth:int=2; cache_max_entries:int=128; cache_max_bytes:int=4*1024*1024
    persistent_cache_max_bytes:int=16*1024*1024; trusted_paths:list[str]=field(default_factory=list); python_timeout:int=120; terminal_timeout:int=30; web_timeout:int=12
    browser_enabled:bool=True; openai_enabled:bool=False; openai_model:str="gpt-5.6-luna"; airllm_model_dir:str="data/models"; airllm_unload_idle_seconds:int=300
    openinterpreter_enabled:bool=True; openinterpreter_timeout:int=180; openinterpreter_model:str="qwen3:0.6b"; openinterpreter_provider:str="ollama"; computer_autopilot_steps:int=8
    profile:dict=field(default_factory=dict)
    @classmethod
    def load(cls):
        s=cls(); e=os.getenv; s.general_model=e("GENERAL_MODEL",s.general_model); s.coding_model=e("CODING_MODEL",s.coding_model); s.model_backend=e("MODEL_BACKEND",s.model_backend).lower()
        s.ollama_url=e("OLLAMA_URL",s.ollama_url).rstrip("/"); s.ollama_general_model=e("OLLAMA_GENERAL_MODEL",s.ollama_general_model); s.ollama_coding_model=e("OLLAMA_CODING_MODEL",s.ollama_coding_model)
        s.low_ram_mode=e("LOW_RAM_MODE","true").lower() in {"1","true","yes","on"}; s.ram_soft_limit_gb=float(e("RAM_SOFT_LIMIT_GB",s.ram_soft_limit_gb)); s.ram_critical_limit_gb=float(e("RAM_CRITICAL_LIMIT_GB",s.ram_critical_limit_gb))
        s.max_context_tokens=int(e("MAX_CONTEXT_TOKENS",768 if s.low_ram_mode else 1024)); s.max_new_tokens=int(e("MAX_NEW_TOKENS",128 if s.low_ram_mode else 192))
        s.max_subagents=int(e("MAX_SUBAGENTS",s.max_subagents)); s.max_parallel_agents=int(e("MAX_PARALLEL_AGENTS",s.max_parallel_agents)); s.max_agent_depth=int(e("MAX_AGENT_DEPTH",s.max_agent_depth))
        s.cache_max_entries=int(e("CACHE_MAX_ENTRIES",s.cache_max_entries)); s.cache_max_bytes=int(e("CACHE_MAX_BYTES",s.cache_max_bytes)); s.persistent_cache_max_bytes=int(e("PERSISTENT_CACHE_MAX_BYTES",s.persistent_cache_max_bytes))
        s.python_timeout=int(e("PYTHON_TIMEOUT",s.python_timeout)); s.terminal_timeout=int(e("TERMINAL_TIMEOUT",s.terminal_timeout)); s.web_timeout=int(e("WEB_TIMEOUT",s.web_timeout)); s.airllm_model_dir=e("AIRLLM_MODEL_DIR",s.airllm_model_dir); s.airllm_unload_idle_seconds=int(e("AIRLLM_UNLOAD_IDLE_SECONDS",s.airllm_unload_idle_seconds))
        raw=e("TRUSTED_PATHS",""); s.trusted_paths=[str(Path(x).expanduser().resolve()) for x in raw.split(os.pathsep) if x.strip()] or [str(ROOT/"scripts"),str(ROOT/"projects")]
        s.openai_enabled=e("OPENAI_ENABLED","false").lower() in {"1","true","yes","on"}; s.openai_model=e("OPENAI_MODEL",s.openai_model)
        s.openinterpreter_enabled=e("OPENINTERPRETER_ENABLED","true").lower() in {"1","true","yes","on"}
        s.openinterpreter_timeout=int(e("OPENINTERPRETER_TIMEOUT",s.openinterpreter_timeout)); s.openinterpreter_model=e("OPENINTERPRETER_MODEL",s.openinterpreter_model); s.openinterpreter_provider=e("OPENINTERPRETER_PROVIDER",s.openinterpreter_provider)
        s.computer_autopilot_steps=int(e("COMPUTER_AUTOPILOT_STEPS",s.computer_autopilot_steps)); s.profile=load_profile(); return s
def load_profile():
    p=CONFIG_DIR/"profile.json"
    try:return json.loads(p.read_text(encoding="utf-8"))
    except Exception:return {"name":"User","assistant_name":"JARVIS","welcome_enabled":True,"welcome_style":"brief","interests":[],"preferred_language":"English"}
