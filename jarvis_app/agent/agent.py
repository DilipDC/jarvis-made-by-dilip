from __future__ import annotations
import re, time
from .fast_intent import classify
from ..tools.system import system_info, open_application
from ..tools.base import ToolRegistry, ToolSpec
from ..tasks.manager import TaskManager
from ..models.router import ModelRouter

class JarvisAgent:
    def __init__(self, settings, store, cache, ollama, router, pyexec, terminal, rag, web, computer, browser, mcp, voice, vision, perms, scheduler, events, openai_agent=None):
        self.s=settings; self.openai_agent=openai_agent; self.store=store; self.cache=cache; self.ollama=ollama; self.router=router; self.pyexec=pyexec; self.terminal=terminal; self.rag=rag; self.web=web; self.computer=computer; self.browser=browser; self.mcp=mcp; self.voice=voice; self.vision=vision; self.perms=perms; self.scheduler=scheduler; self.events=events; self.tasks=TaskManager(store,events); self.pending={}; self.tools=ToolRegistry(); self._register_tools()
    def _register_tools(self):
        self.tools.register(ToolSpec('system_info','CPU, RAM, disk, platform and clock','SAFE',handler=lambda **_:system_info()))
        self.tools.register(ToolSpec('remember','Persist an explicit user memory','SAFE',handler=lambda content,**_:self.store.remember(content,kind='user_requested',importance=3)))
        self.tools.register(ToolSpec('web_search','Search current web information','SAFE',handler=lambda query,**_:self.web.search(query)))
        self.tools.register(ToolSpec('open_application','Launch an application','SAFE',handler=lambda name,**_:open_application(name)))
        self.tools.register(ToolSpec('execute_python','Run an existing trusted Python file','CONFIRM',handler=None))
        self.tools.register(ToolSpec('run_terminal','Run an OS command','CONFIRM',handler=None))
        self.tools.register(ToolSpec('read_memory','Retrieve persistent memory','SAFE',handler=lambda query,**_:self.store.search(query,10)))
        self.tools.register(ToolSpec('search_rag','Search ingested documents','SAFE',handler=lambda query,**_:self.rag.search(query,8)))
        self.tools.register(ToolSpec('browser_title','Open a URL headlessly and read its title','SAFE',handler=lambda url,**_:self.browser.fetch_title(url)))
    def status(self):
        oi=self.ollama.health(); info=system_info()
        return {
            'online':True,
            'model':{'available':oi['available'],'models':[m.get('name') for m in oi.get('models',[])], 'general':self.s.general_model,'coding':self.s.coding_model},
            'memory':{'available':True},'rag':{'available':True},'mcp':self.mcp.health(),'web':{'available':True},
            'system':info,'voice':self.voice.health(),'computer':self.computer.health(),'python':{'available':True,'trusted_paths':self.s.trusted_paths},
            'browser':self.browser.health(),'scheduler':{'available':True,'tasks':len(self.scheduler.list())},'cache':self.cache.stats(),'tasks':self.tasks.list()[:20],
            'profile':self.s.profile,'openai': self.openai_agent.status() if self.openai_agent else {'available':False},
        }
    def _emit(self,event,**payload): return self.events.emit(event,**payload)
    def _confirmation(self, action,target,reason, callback):
        import uuid
        cid=str(uuid.uuid4()); self.pending[cid]={'id':cid,'action':action,'target':target,'reason':reason,'callback':callback,'created_at':time.time()}; self._emit('confirmation.required', confirmation=self.pending[cid].copy()); return cid
    def confirm(self,cid,approved:bool):
        item=self.pending.pop(cid,None)
        if not item: return {'ok':False,'error':'confirmation not found'}
        if not approved: self._emit('confirmation.denied',confirmation_id=cid); return {'ok':True,'approved':False,'text':'Action cancelled.'}
        try: result=item['callback'](); self._emit('confirmation.approved',confirmation_id=cid,result=result); return {'ok':True,'approved':True,'result':result}
        except Exception as e: self._emit('confirmation.failed',confirmation_id=cid,error=str(e)); return {'ok':False,'error':str(e)}
    def chat(self,text:str):
        text=text.strip(); started=time.perf_counter(); intent=classify(text); task=self.tasks.create(text[:80]); self.tasks.update(task.task_id,'PLANNING',detail=f'Intent: {intent}'); self._emit('agent.state',state='THINKING',intent=intent,task_id=task.task_id)
        self.store.audit('intent','SAFE',intent)
        try:
            result=self._dispatch(text,intent,task.task_id)
            self.tasks.update(task.task_id,'COMPLETED',1.0,'Verified response')
            result['task_id']=task.task_id; result['latency_ms']=round((time.perf_counter()-started)*1000,2); self._emit('agent.completed',result=result); return result
        except Exception as e:
            self.tasks.update(task.task_id,'FAILED',detail='Unhandled agent error',error=str(e)); self._emit('agent.error',error=str(e),task_id=task.task_id); return {'text':f'JARVIS error: {e}','intent':intent,'task_id':task.task_id,'error':str(e)}
    def _dispatch(self,text,intent,task_id):
        if intent in {'ram','cpu'}:
            self.tasks.update(task_id,'EXECUTING',detail='Reading OS metrics'); info=system_info();
            text_out = f"CPU {info.get('cpu_percent','n/a')}% | RAM {info.get('ram_percent','n/a')}%" if intent=='ram' else f"CPU {info.get('cpu_percent','n/a')}% | {info.get('cpu_count','n/a')} logical CPUs"
            return {'text':text_out,'intent':intent,'source':'OS API','data':info}
        if intent=='time': return {'text':system_info()['time'],'intent':intent,'source':'system clock'}
        if intent=='status': return {'text':'JARVIS is online. Use the SYSTEM panel for live subsystem health.','intent':intent,'source':'health checks','data':self.status()}
        if intent=='remember':
            content=text.split(None,1)[1] if len(text.split(None,1))>1 else ''
            self.store.remember(content,kind='user_requested',importance=3); return {'text':'Memory stored.','intent':intent,'source':'SQLite'}
        if intent=='forget':
            q=text.split(None,1)[1] if len(text.split(None,1))>1 else ''; return {'text':f'Removed {self.store.forget(q)} matching memory record(s).','intent':intent,'source':'SQLite'}
        if intent=='python':
            m=re.search(r'([\w./\\-]+\.py)(?:\s+(.*))?$',text); script=m.group(1) if m else ''
            decision=self.perms.check('execute python',script)
            if decision.level!='SAFE':
                cid=self._confirmation('execute python',script,decision.reason,lambda:self.pyexec.run_script(script,(m.group(2) or '').split() if m else []))
                self.tasks.update(task_id,'WAITING_CONFIRMATION',detail='Waiting for Python execution approval')
                return {'text':f'Confirmation required to execute {script}.','intent':intent,'permission':decision.level,'confirmation_id':cid}
            result=self.pyexec.run_script(script,(m.group(2) or '').split() if m else []); return {'text':f'Started {result["script"]} as PID {result["pid"]}','intent':intent,'source':'PythonExecutionManager','task':result}
        if intent=='open_app':
            target=text.split(None,1)[1].strip(); result=open_application(target); return {'text':f'Launch requested for {target}.','intent':intent,'verification':result}
        if intent=='list_tasks': return {'text':'\n'.join(f"{x['script']} · {x['status']} · PID {x['pid']}" for x in self.pyexec.list()) or 'No Python tasks running or recorded.','intent':intent,'tasks':self.pyexec.list()}
        if intent=='terminal':
            cmd=text.split(None,2)[-1] if len(text.split(None,2))>=3 else ''
            decision=self.perms.check('run terminal',cmd)
            if decision.level!='SAFE':
                cid=self._confirmation('run terminal',cmd,decision.reason,lambda:self.terminal.run_line(cmd))
                return {'text':'Confirmation required before running a terminal command.','intent':intent,'permission':decision.level,'confirmation_id':cid}
            r=self.terminal.run_line(cmd); return {'text':r.stdout or r.stderr,'intent':intent,'source':'terminal','returncode':r.returncode,'stderr':r.stderr}
        if intent=='web':
            self.tasks.update(task_id,'EXECUTING',detail='Searching live web'); r=self.web.search(text); return {'text':'\n'.join(f"{x['title']} — {x['url']}" for x in r['results']) or 'No web results found.','intent':intent,'source':'live web','results':r['results']}
        # RAG first for project/document questions
        if re.search(r'\b(project|documentation|docs|memory|what did i|remembered)\b',text,re.I):
            hits=self.rag.search(text,5) or self.store.search(text,5)
            if hits: return {'text':'Relevant local knowledge:\n'+'\n'.join((h.get('content') or h.get('title') or '')[:700] for h in hits),'intent':'rag','source':'local knowledge','hits':hits}
        model=self.router.route(text); hits=self.store.search(text,4)
        messages=[{'role':'system','content':f'You are JARVIS, a precise local-first assistant. Current model role: {self.router.classify(text)}. Never claim actions you did not perform. Prefer concise answers and clearly state uncertainty.'}]
        if hits: messages.append({'role':'system','content':'Relevant memory:\n'+'\n'.join(h['content'] for h in hits)})
        messages.append({'role':'user','content':text}); self.tasks.update(task_id,'EXECUTING',detail=f'Calling {model}')
        r=self.ollama.chat(model,messages,False)
        if isinstance(r,tuple): r=r[0]
        msg=r.get('message',{}).get('content','')
        return {'text':msg or 'No response returned by the local model.','intent':intent,'model':model,'latency_ms':r.get('_latency_ms')}
    def stream_chat(self,text):
        # deterministic fast path is returned as one event; model responses stream chunk-by-chunk.
        intent=classify(text)
        if intent in {'ram','cpu','time','remember','forget','status','python','open_app','list_tasks','web'}:
            yield {'type':'final','data':self.chat(text)}; return
        model=self.router.route(text); hits=self.store.search(text,4); messages=[{'role':'system','content':'You are JARVIS, a precise local-first assistant. Never claim actions you did not perform.'}]
        if hits: messages.append({'role':'system','content':'Relevant memory:\n'+'\n'.join(h['content'] for h in hits)})
        messages.append({'role':'user','content':text})
        self._emit('agent.state',state='SPEAKING',model=model)
        try:
            full=''
            for chunk in self.ollama.stream_chat(model,messages):
                piece=chunk.get('message',{}).get('content','')
                if piece: full+=piece; yield {'type':'delta','data':piece}
            yield {'type':'final','data':{'text':full,'intent':intent,'model':model}}
        except Exception as e:
            yield {'type':'final','data':{'text':f'Local model unavailable: {e}','error':str(e),'intent':intent,'model':model}}
