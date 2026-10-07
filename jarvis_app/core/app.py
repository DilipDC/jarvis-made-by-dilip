from __future__ import annotations
import asyncio,json
from pathlib import Path
from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi.responses import HTMLResponse,StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .config import DATA_DIR,Settings
from .resources import snapshot
from .identity import IDENTITY
from ..agent.agent import JarvisAgent
from ..agents.builtins import build_agent_manager
from ..browser.manager import BrowserManager
from ..cache.cache import CacheManager
from ..computer.manager import ComputerControlManager
from ..events.bus import EventBus
from ..mcp.manager import MCPManager
from ..memory.sqlite import MemoryStore
from ..models.airllm_client import AirLLMClient
from ..models.ollama import OllamaClient
from ..models.openai_agents_adapter import OpenAIAgentsAdapter
from ..models.router import ModelRouter
from ..policy.loader import load_policy
from ..python_exec.manager import PythonExecutionManager
from ..rag.manager import RAGManager
from ..scheduler.scheduler import Scheduler
from ..security.permissions import PermissionManager
from ..terminal.manager import TerminalManager
from ..vision.manager import VisionManager
from ..voice.manager import VoiceManager
from ..web.search import WebSearch
settings=Settings.load(); DATA_DIR.mkdir(exist_ok=True); events=EventBus()
store=MemoryStore(DATA_DIR/"jarvis.sqlite3")
if not store.search("JARVIS identity",1):
    store.remember("JARVIS identity: "+json.dumps(IDENTITY,ensure_ascii=False),kind="jarvis_identity",importance=5,tags=["identity","creator","capabilities"])
cache=CacheManager(settings.cache_max_entries,settings.cache_max_bytes,settings.persistent_cache_max_bytes,DATA_DIR/"cache")
airllm=AirLLMClient(DATA_DIR/"models",settings.max_context_tokens,settings.max_new_tokens,settings.airllm_unload_idle_seconds)
ollama=OllamaClient(settings.ollama_url,settings.model_backend,airllm,settings.ollama_general_model,settings.ollama_coding_model)
router=ModelRouter(settings.general_model,settings.coding_model); pyexec=PythonExecutionManager(settings.trusted_paths,settings.python_timeout,store); terminal=TerminalManager(settings.terminal_timeout)
openai_agent=OpenAIAgentsAdapter(settings.openai_model); rag=RAGManager(store); web=WebSearch(settings.web_timeout); computer=ComputerControlManager(); browser=BrowserManager(); mcp=MCPManager(); voice=VoiceManager(); vision=VisionManager(); scheduler=Scheduler(store,events)
policy=load_policy(Path(__file__).resolve().parents[2]); perms=PermissionManager(policy)
agent_manager=build_agent_manager(settings.general_model,settings.coding_model,settings.max_subagents,settings.max_parallel_agents,settings.max_agent_depth)
agent=JarvisAgent(settings,store,cache,ollama,router,pyexec,terminal,rag,web,computer,browser,mcp,voice,vision,perms,scheduler,events,openai_agent,agent_manager=agent_manager)
app=FastAPI(title="JARVIS — BUILT BY DILIP",version="1.0.1"); ROOT=Path(__file__).resolve().parents[2]; app.mount("/ui",StaticFiles(directory=str(ROOT/"ui")),name="ui")
class Chat(BaseModel):text:str
class MemoryIn(BaseModel):text:str
class Confirmation(BaseModel):approved:bool
class ScheduleIn(BaseModel):delay_seconds:int; command:str
class ComputerAction(BaseModel):action:str; x:int|None=None; y:int|None=None; text:str|None=None; key:str|None=None; keys:str|None=None; path:str|None=None
@app.get("/",response_class=HTMLResponse)
def index():return (ROOT/"ui"/"index.html").read_text(encoding="utf-8")
@app.get("/api/status")
def status():
    r=agent.status(); r["resources"]=snapshot(settings.ram_soft_limit_gb,settings.ram_critical_limit_gb); return r
@app.get("/api/doctor")
def doctor():
    s=agent.status(); checks={"python":"PASS","sqlite":"PASS" if s["memory"]["available"] else "FAIL","model_gateway":"PASS" if s["model"]["available"] else "WARN","airllm":"PASS" if s["model"].get("airllm",{}).get("available") else "WARN","ollama_fallback":"PASS" if s["model"].get("ollama",{}).get("available") else "WARN","browser":"PASS" if s["browser"]["available"] else "WARN","mcp":"PASS" if s["mcp"].get("available") else "WARN","voice":"PASS" if s["voice"].get("stt") or s["voice"].get("tts") else "WARN","network":"PASS" if s["web"]["available"] else "WARN","policy":"PASS" if s.get("policy",{}).get("available") else "WARN","agents":"PASS" if s.get("agents",{}).get("available") else "WARN"}; return {"status":"PASS" if "FAIL" not in checks.values() else "FAIL","checks":checks}
@app.get("/api/agents")
def agents():return agent.agent_manager.snapshot()
@app.post("/api/chat")
def chat(body:Chat):return agent.chat(body.text)
@app.get("/api/chat/stream")
def stream(text:str):
    def gen():
        for item in agent.stream_chat(text):yield (json.dumps(item,ensure_ascii=False,default=str)+"\n").encode()
    return StreamingResponse(gen(),media_type="application/x-ndjson")
@app.get("/api/tasks")
def tasks():return {"python":pyexec.list(),"agent":agent.tasks.list()}
@app.post("/api/tasks/{task_id}/stop")
def stop_task(task_id:str):return pyexec.stop(task_id)
@app.get("/api/memory")
def memory(q:str=""):return store.search(q,20)
@app.post("/api/memory")
def remember(body:MemoryIn):return {"id":store.remember(body.text,kind="user_requested",importance=3)}
@app.get("/api/identity")
def identity():return __import__("jarvis_app.core.identity",fromlist=["describe_identity"]).describe_identity()
@app.get("/api/tools")
def tools():return agent.tools.describe()
@app.get("/api/mcp")
def mcp_status():return mcp.health()
@app.post("/api/mcp/{name}/inspect")
async def mcp_inspect(name:str):return await mcp.inspect(name)
@app.get("/api/cache")
def cache_stats():return cache.stats()
@app.post("/api/cache/temp/clear")
def cache_clear_temp():cache.clear_temp(); return {"ok":True,"cache":cache.stats()}
@app.get("/api/confirmations")
def confirmations():return [{k:v for k,v in x.items() if k!="callback"} for x in agent.pending.values()]
@app.post("/api/confirmations/{cid}")
def confirm(cid:str,body:Confirmation):return agent.confirm(cid,body.approved)
@app.get("/api/schedule")
def schedule():return scheduler.list()
@app.post("/api/schedule")
def add_schedule(body:ScheduleIn):return scheduler.add(body.delay_seconds,body.command)
@app.delete("/api/schedule/{tid}")
def cancel_schedule(tid:str):return {"cancelled":scheduler.cancel(tid)}
@app.post("/api/terminal")
def terminal_endpoint(body:Chat):return agent.chat("run command "+body.text)
@app.post("/api/computer")
def computer_endpoint(body:ComputerAction):return computer.act(body.action,x=body.x,y=body.y,text=body.text,key=body.key,keys=body.keys,path=body.path)
@app.post("/api/rag/ingest")
def ingest(path:str):return rag.ingest(path)
@app.get("/api/rag/search")
def rag_search(q:str,limit:int=8):return rag.search(q,limit)
_clients:set[asyncio.Queue]=set()
def bridge(data):
    for q in list(_clients):
        try:q.put_nowait(data)
        except Exception:pass
for event_name in ["agent.state","agent.completed","agent.error","task.created","task.updated","confirmation.required","confirmation.approved","confirmation.denied","confirmation.failed","scheduler.add","scheduler.cancel","scheduler.due"]:events.on(event_name,bridge)
@app.websocket("/api/events")
async def ws(websocket:WebSocket):
    await websocket.accept(); q=asyncio.Queue(); _clients.add(q)
    try:
        await websocket.send_json({"event":"connected","status":"ONLINE"})
        while True:
            try:await websocket.send_json(await asyncio.wait_for(q.get(),timeout=20))
            except asyncio.TimeoutError:await websocket.send_json({"event":"heartbeat"})
    except WebSocketDisconnect:pass
    finally:_clients.discard(q)
