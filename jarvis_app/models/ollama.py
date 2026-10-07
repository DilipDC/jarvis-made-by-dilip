from __future__ import annotations
import json,time
import httpx
from .airllm_client import AirLLMClient

class _OllamaHTTPClient:
    def __init__(self,base_url):self.base_url=base_url.rstrip("/")
    def health(self):
        try:
            r=httpx.get(f"{self.base_url}/api/tags",timeout=2); r.raise_for_status(); return {"available":True,"models":r.json().get("models",[]),"backend":"ollama"}
        except Exception as exc:return {"available":False,"models":[],"backend":"ollama","error":str(exc)}
    def chat(self,model,messages,stream=False):
        start=time.perf_counter(); r=httpx.post(f"{self.base_url}/api/chat",json={"model":model,"messages":messages,"stream":stream},timeout=180); r.raise_for_status(); data=r.json(); data["_latency_ms"]=round((time.perf_counter()-start)*1000,2); data["_backend"]="ollama"; return data
    def stream_chat(self,model,messages):
        with httpx.stream("POST",f"{self.base_url}/api/chat",json={"model":model,"messages":messages,"stream":True},timeout=180) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:yield json.loads(line)

class OllamaClient:
    def __init__(self,base_url,backend="airllm",airllm=None,ollama_general="qwen3:0.6b",ollama_coding="qwen2.5-coder:1.5b"):
        self.base_url=base_url; self.backend=backend; self.airllm=airllm or AirLLMClient(); self.ollama=_OllamaHTTPClient(base_url)
        self.ollama_general=ollama_general; self.ollama_coding=ollama_coding; self._last_backend=backend
    def _ollama_model(self,model):return self.ollama_coding if model.startswith("Qwen/") and "Coder" in model else (self.ollama_general if model.startswith("Qwen/") else model)
    def health(self):
        air=self.airllm.health(); oll=self.ollama.health(); pref=air["available"] if self.backend in {"airllm","auto"} else oll["available"]
        return {"available":pref or oll["available"],"backend":self._last_backend,"preferred_backend":self.backend,"airllm":air,"ollama":oll,"models":oll.get("models",[])}
    def chat(self,model,messages,stream=False):
        if self.backend in {"airllm","auto"} and self.airllm.available:
            try:self._last_backend="airllm"; return self.airllm.chat(model,messages,stream)
            except Exception:
                if self.backend=="airllm" and self.ollama.health()["available"]:self._last_backend="ollama"; return self.ollama.chat(self._ollama_model(model),messages)
                raise
        self._last_backend="ollama"; return self.ollama.chat(self._ollama_model(model),messages)
    def stream_chat(self,model,messages):
        if self.backend in {"airllm","auto"} and self.airllm.available:
            try:self._last_backend="airllm"; yield from self.airllm.stream_chat(model,messages); return
            except Exception:
                if self.backend=="airllm" and not self.ollama.health()["available"]:raise
        self._last_backend="ollama"; yield from self.ollama.stream_chat(self._ollama_model(model),messages)
    def unload_inactive(self):self.airllm.unload()
