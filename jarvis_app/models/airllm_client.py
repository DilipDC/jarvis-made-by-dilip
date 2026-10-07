from __future__ import annotations
import gc, importlib.util, threading, time
from pathlib import Path

class AirLLMClient:
    def __init__(self,models_root="data/models",max_context=768,max_new_tokens=192,unload_idle_seconds=300):
        self.models_root=Path(models_root); self.models_root.mkdir(parents=True,exist_ok=True)
        self.max_context=max_context; self.max_new_tokens=max_new_tokens; self.unload_idle_seconds=unload_idle_seconds
        self._model=None; self._model_name=None; self._lock=threading.RLock(); self._last_used=0.0; self._load_error=None
    @property
    def available(self):return importlib.util.find_spec("airllm") is not None
    def health(self):return {"available":self.available,"backend":"airllm","loaded_model":self._model_name,"last_error":self._load_error,"lazy_loading":True,"max_context":self.max_context,"max_new_tokens":self.max_new_tokens}
    def _device(self):
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:return "cpu"
    def unload(self):
        with self._lock:
            self._model=None; self._model_name=None; self._last_used=0.0; gc.collect()
            try:
                import torch
                if torch.cuda.is_available():torch.cuda.empty_cache()
            except Exception:pass
    def _maybe_unload_idle(self):
        if self._model is not None and self._last_used and time.time()-self._last_used>self.unload_idle_seconds:self.unload()
    def _load(self,model_name):
        with self._lock:
            self._maybe_unload_idle()
            if self._model is not None and self._model_name==model_name:self._last_used=time.time(); return self._model
            self.unload()
            if not self.available:raise RuntimeError("AirLLM is not installed. Install with: pip install -e ".[airllm]"")
            try:
                from airllm import AutoModel
                self._model=AutoModel.from_pretrained(model_name,layer_shards_saving_path=str(self.models_root))
                self._model_name=model_name; self._last_used=time.time(); self._load_error=None; return self._model
            except Exception as exc:
                self._load_error=str(exc); self.unload(); raise
    def _prompt(self,model,messages):
        tok=model.tokenizer
        if hasattr(tok,"apply_chat_template"):
            try:return tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
            except TypeError:return tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        return "\n".join(f"{m['role']}: {m['content']}" for m in messages)+"\nassistant:"
    def chat(self,model_name,messages,stream=False):
        del stream
        start=time.perf_counter(); model=self._load(model_name); tok=model.tokenizer; prompt=self._prompt(model,messages)
        tokens=tok([prompt],return_tensors="pt",return_attention_mask=False,truncation=True,max_length=self.max_context,padding=False)
        input_ids=tokens["input_ids"].to(self._device())
        out=model.generate(input_ids,max_new_tokens=self.max_new_tokens,use_cache=True,return_dict_in_generate=True)
        text=tok.decode(out.sequences[0,input_ids.shape[1]:],skip_special_tokens=True).strip(); self._last_used=time.time()
        return {"message":{"role":"assistant","content":text},"_latency_ms":round((time.perf_counter()-start)*1000,2),"_backend":"airllm","_model":model_name}
    def stream_chat(self,model_name,messages):
        r=self.chat(model_name,messages); yield {"message":{"role":"assistant","content":r["message"]["content"]}}
