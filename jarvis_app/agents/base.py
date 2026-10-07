from __future__ import annotations
import time,uuid
from dataclasses import dataclass,field
from typing import Any,Callable
@dataclass(slots=True)
class AgentTask:
    task_id:str; agent:str; input:str; created_at:float=field(default_factory=time.time); started_at:float|None=None; ended_at:float|None=None; status:str="queued"; confidence:float=0.0; result:Any=None; error:str|None=None
@dataclass(slots=True)
class AgentSpec:
    name:str; description:str; capabilities:tuple[str,...]; model:str; priority:int=50; timeout:float=30; max_context_tokens:int=768; cache_policy:str="temp"
class BaseAgent:
    def __init__(self,spec:AgentSpec,handler:Callable[...,Any]|None=None):self.spec=spec; self.handler=handler
    def execute(self,text:str,**kwargs):
        task=AgentTask(str(uuid.uuid4()),self.spec.name,text,started_at=time.time(),status="running")
        try:task.result=self.handler(text,**kwargs) if self.handler else None; task.status="completed"; task.confidence=1.0 if task.result is not None else 0.5
        except Exception as exc:task.status="failed"; task.error=str(exc)
        task.ended_at=time.time(); return task
