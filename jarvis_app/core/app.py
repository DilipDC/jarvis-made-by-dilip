from __future__ import annotations
import asyncio, json
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .config import Settings,DATA_DIR
from ..memory.sqlite import MemoryStore
from ..cache.cache import CacheManager
from ..models.ollama import OllamaClient
from ..models.router import ModelRouter
from ..models.openai_agents_adapter import OpenAIAgentsAdapter
from ..python_exec.manager import PythonExecutionManager
from ..terminal.manager import TerminalManager
from ..rag.manager import RAGManager
from ..web.search import WebSearch
from ..computer.manager import ComputerControlManager
from ..browser.manager import BrowserManager
from ..mcp.manager import MCPManager
from ..voice.manager import VoiceManager
from ..vision.manager import VisionManager
from ..scheduler.scheduler import Scheduler
from ..security.permissions import PermissionManager
from ..events.bus import EventBus
from ..agent.agent import JarvisAgent

settings=Settings.load(); DATA_DIR.mkdir(exist_ok=True); events=EventBus()
store=MemoryStore(DATA_DIR/'jarvis.sqlite3'); cache=CacheManager(settings.cache_max_entries,settings.cache_max_bytes); ollama=OllamaClient(settings.ollama_url); router=ModelRouter(settings.general_model,settings.coding_model)
pyexec=PythonExecutionManager(settings.trusted_paths,settings.python_timeout,store); terminal=TerminalManager(settings.terminal_timeout); openai_agent=OpenAIAgentsAdapter(settings.openai_model); rag=RAGManager(store); web=WebSearch(settings.web_timeout); computer=ComputerControlManager(); browser=BrowserManager(); mcp=MCPManager(); voice=VoiceManager(); vision=VisionManager(); scheduler=Scheduler(store,events); perms=PermissionManager()
agent=JarvisAgent(settings,store,cache,ollama,router,pyexec,terminal,rag,web,computer,browser,mcp,voice,vision,perms,scheduler,events,openai_agent)
app=FastAPI(title='JARVIS — BUILT BY DILIP',version='0.2.0')
ROOT=Path(__file__).resolve().parents[2]; app.mount('/ui',StaticFiles(directory=str(ROOT/'ui')),name='ui')

class Chat(BaseModel): text:str
class MemoryIn(BaseModel): text:str
class Confirmation(BaseModel): approved:bool
class ScheduleIn(BaseModel): delay_seconds:int; command:str

@app.get('/',response_class=HTMLResponse)
def index(): return (ROOT/'ui'/'index.html').read_text(encoding='utf-8')
@app.get('/api/status')
def status(): return agent.status()
@app.get('/api/doctor')
def doctor():
    s=agent.status(); checks={}
    checks['python']='PASS'; checks['sqlite']='PASS' if s['memory']['available'] else 'FAIL'; checks['ollama']='PASS' if s['model']['available'] else 'WARN'; checks['browser']='PASS' if s['browser']['available'] else 'WARN'; checks['mcp']='PASS' if s['mcp'].get('available') else 'WARN'; checks['voice']='PASS' if s['voice'].get('stt') or s['voice'].get('tts') else 'WARN'; checks['network']='PASS' if s['web']['available'] else 'WARN'; return {'status':'PASS' if 'FAIL' not in checks.values() else 'FAIL','checks':checks}
@app.post('/api/chat')
def chat(body:Chat): return agent.chat(body.text)
@app.get('/api/chat/stream')
def stream(text:str):
    def gen():
        for item in agent.stream_chat(text): yield (json.dumps(item,ensure_ascii=False,default=str)+'\n').encode()
    return StreamingResponse(gen(),media_type='application/x-ndjson')
@app.get('/api/tasks')
def tasks(): return {'python':pyexec.list(),'agent':agent.tasks.list()}
@app.post('/api/tasks/{task_id}/stop')
def stop_task(task_id:str): return pyexec.stop(task_id)
@app.get('/api/memory')
def memory(q:str=''): return store.search(q,20)
@app.post('/api/memory')
def remember(body:MemoryIn): return {'id':store.remember(body.text,kind='user_requested',importance=3)}
@app.get('/api/tools')
def tools(): return agent.tools.describe()
@app.get('/api/confirmations')
def confirmations(): return [dict((k,v) for k,v in x.items() if k!='callback') for x in agent.pending.values()]
@app.post('/api/confirmations/{cid}')
def confirm(cid:str,body:Confirmation): return agent.confirm(cid,body.approved)
@app.get('/api/schedule')
def schedule(): return scheduler.list()
@app.post('/api/schedule')
def add_schedule(body:ScheduleIn): return scheduler.add(body.delay_seconds,body.command)
@app.delete('/api/schedule/{tid}')
def cancel_schedule(tid:str): return {'cancelled':scheduler.cancel(tid)}
@app.post('/api/terminal')
def terminal(body:Chat): return agent.chat('run command '+body.text)
@app.post('/api/rag/ingest')
def ingest(path:str): return rag.ingest(path)
@app.get('/api/rag/search')
def rag_search(q:str,limit:int=8): return rag.search(q,limit)

_clients:set[asyncio.Queue]=set()
def bridge(data):
    for q in list(_clients):
        try: q.put_nowait(data)
        except Exception: pass
for event_name in ['agent.state','agent.completed','agent.error','task.created','task.updated','confirmation.required','confirmation.approved','confirmation.denied','confirmation.failed','scheduler.add','scheduler.cancel','scheduler.due']:
    events.on(event_name,bridge)

@app.websocket('/api/events')
async def ws(websocket:WebSocket):
    await websocket.accept(); q=asyncio.Queue(); _clients.add(q)
    try:
        await websocket.send_json({'event':'connected','status':'ONLINE'})
        while True:
            try:
                data=await asyncio.wait_for(q.get(),timeout=20)
                await websocket.send_json(data)
            except asyncio.TimeoutError:
                await websocket.send_json({'event':'heartbeat'})
    except WebSocketDisconnect:
        pass
    finally:
        _clients.discard(q)
