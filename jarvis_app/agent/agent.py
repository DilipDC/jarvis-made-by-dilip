from __future__ import annotations
import re,time
from ..agents.manager import AgentManager
from ..core.resources import low_ram_cleanup,snapshot
from ..models.router import ModelRouter
from ..tasks.manager import TaskManager
from ..tools.base import ToolRegistry,ToolSpec
from ..tools.system import open_application,system_info
from ..web.research import WebResearchAgent
from ..core.identity import answer_identity
from .fast_intent import classify
class JarvisAgent:
    def __init__(self,settings,store,cache,ollama,router,pyexec,terminal,rag,web,computer,browser,mcp,voice,vision,perms,scheduler,events,openai_agent=None,agent_manager:AgentManager|None=None):
        self.s=settings; self.openai_agent=openai_agent; self.store=store; self.cache=cache; self.ollama=ollama; self.router:ModelRouter=router; self.pyexec=pyexec; self.terminal=terminal; self.rag=rag; self.web=web; self.computer=computer; self.browser=browser; self.mcp=mcp; self.voice=voice; self.vision=vision; self.perms=perms; self.scheduler=scheduler; self.events=events; self.tasks=TaskManager(store,events); self.agent_manager=agent_manager; self.pending={}; self.tools=ToolRegistry(); self.researcher=WebResearchAgent(web,settings.web_timeout); self._register_tools()
    def _register_tools(self):
        self.tools.register(ToolSpec("system_info","CPU, RAM, disk, platform and clock","SAFE",handler=lambda **_:system_info()))
        self.tools.register(ToolSpec("remember","Persist an explicit user memory","SAFE",handler=lambda content,**_:self.store.remember(content,kind="user_requested",importance=3)))
        self.tools.register(ToolSpec("web_search","Search current web information","SAFE",handler=lambda query,**_:self.web.search(query)))
        self.tools.register(ToolSpec("web_research","Search, read, synthesize and cite public web sources","SAFE",handler=lambda query,**_:self.researcher.research(query,self.ollama,self.router.route(query),self.cache)))
        self.tools.register(ToolSpec("open_application","Launch an application","SAFE",handler=lambda name,**_:open_application(name)))
        self.tools.register(ToolSpec("execute_python","Run an existing trusted Python file","CONFIRM",handler=None))
        self.tools.register(ToolSpec("run_terminal","Run an OS command","CONFIRM",handler=None))
        self.tools.register(ToolSpec("read_memory","Retrieve persistent memory","SAFE",handler=lambda query,**_:self.store.search(query,10)))
        self.tools.register(ToolSpec("search_rag","Search ingested documents","SAFE",handler=lambda query,**_:self.rag.search(query,8)))
        self.tools.register(ToolSpec("browser_title","Open a URL headlessly and read its title","SAFE",handler=lambda url,**_:self.browser.fetch_title(url)))
        self.tools.register(ToolSpec("computer_control","Approved desktop control action","CONFIRM",handler=lambda action,**kwargs:self.computer.act(action,**kwargs)))
    def status(self):
        oi=self.ollama.health(); info=system_info()
        return {"online":True,"model":{"available":oi["available"],"backend":oi.get("backend"),"preferred_backend":oi.get("preferred_backend"),"models":[m.get("name") for m in oi.get("models",[])],"general":self.s.general_model,"coding":self.s.coding_model,"airllm":oi.get("airllm",{}),"ollama":oi.get("ollama",{})},"memory":{"available":True},"rag":{"available":True},"mcp":self.mcp.health(),"web":{"available":True},"system":info,"resources":snapshot(self.s.ram_soft_limit_gb,self.s.ram_critical_limit_gb),"voice":self.voice.health(),"computer":self.computer.health(),"python":{"available":True,"trusted_paths":self.s.trusted_paths},"browser":self.browser.health(),"scheduler":{"available":True,"tasks":len(self.scheduler.list())},"cache":self.cache.stats(),"tasks":self.tasks.list()[:20],"profile":self.s.profile,"policy":{"available":self.perms.policy is not None},"agents":self.agent_manager.snapshot() if self.agent_manager else {"available":False,"count":0},"openai":self.openai_agent.status() if self.openai_agent else {"available":False}}
    def _emit(self,event,**payload):return self.events.emit(event,**payload)
    def _confirmation(self,action,target,reason,callback):
        import uuid
        cid=str(uuid.uuid4()); self.pending[cid]={"id":cid,"action":action,"target":target,"reason":reason,"callback":callback,"created_at":time.time()}; self._emit("confirmation.required",confirmation=self.pending[cid].copy()); return cid
    def confirm(self,cid,approved):
        item=self.pending.pop(cid,None)
        if not item:return {"ok":False,"error":"confirmation not found"}
        if not approved:self._emit("confirmation.denied",confirmation_id=cid); return {"ok":True,"approved":False,"text":"Action cancelled."}
        try:r=item["callback"](); self._emit("confirmation.approved",confirmation_id=cid,result=r); return {"ok":True,"approved":True,"result":r}
        except Exception as exc:self._emit("confirmation.failed",confirmation_id=cid,error=str(exc)); return {"ok":False,"error":str(exc)}
    def _selected_agent(self,intent,text):return self.agent_manager.select(intent,text) if self.agent_manager else "CoreAgent"
    def chat(self,text):
        text=text.strip(); start=time.perf_counter(); intent=classify(text); selected=self._selected_agent(intent,text); task=self.tasks.create(text[:80]); self.tasks.update(task.task_id,"PLANNING",detail=f"Intent: {intent} · Agent: {selected}"); self._emit("agent.state",state="THINKING",intent=intent,agent=selected,task_id=task.task_id); self.store.audit("intent","SAFE",f"{intent}:{selected}")
        try:
            result=self._dispatch(text,intent,task.task_id); result["agent"]=selected; self.tasks.update(task.task_id,"COMPLETED",1.0,"Verified response"); result["task_id"]=task.task_id; result["latency_ms"]=round((time.perf_counter()-start)*1000,2); self._emit("agent.completed",result=result); return result
        except Exception as exc:
            self.tasks.update(task.task_id,"FAILED",detail="Unhandled agent error",error=str(exc)); self._emit("agent.error",error=str(exc),task_id=task.task_id); return {"text":f"JARVIS error: {exc}","intent":intent,"agent":selected,"task_id":task.task_id,"error":str(exc)}
    def _dispatch(self,text,intent,task_id):
        identity=answer_identity(text)
        if identity:
            self.store.remember("JARVIS identity: "+identity,kind="jarvis_identity",importance=5)
            return {"text":identity,"intent":"identity","source":"permanent identity profile"}
        if intent=="computer":
            m=re.search(r"click\s+(\d+)\s+(\d+)",text,re.I)
            if m: action,args="click",{"x":int(m.group(1)),"y":int(m.group(2))}
            else:
                m=re.search(r"double\s*click\s+(\d+)\s+(\d+)",text,re.I)
                if m: action,args="double_click",{"x":int(m.group(1)),"y":int(m.group(2))}
                else:
                    m=re.search(r"type\s+(.+)$",text,re.I)
                    if m: action,args="type",{"text":m.group(1)}
                    else:
                        m=re.search(r"press\s+([\w]+)",text,re.I)
                        if m: action,args="press",{"key":m.group(1)}
                        else:
                            m=re.search(r"hotkey\s+([\w+ -]+)",text,re.I)
                            if m: action,args="hotkey",{"keys":m.group(1).replace(" ","")}
                            elif re.search(r"screenshot",text,re.I): action,args="screenshot",{}
                            else: return {"text":"Tell me a desktop action such as click 500 300, type text, press enter, hotkey ctrl+alt+t, or screenshot.","intent":"computer"}
            d=self.perms.check("terminal",f"desktop:{action}")
            if d.level!="SAFE":
                cid=self._confirmation("desktop control",action,d.reason,lambda:self.computer.act(action,**args))
                self.tasks.update(task_id,"WAITING_CONFIRMATION",detail="Waiting for desktop control approval")
                return {"text":f"Confirmation required before desktop action: {action}.","intent":"computer","confirmation_id":cid}
            return {"text":f"Desktop action completed: {action}.","intent":"computer","result":self.computer.act(action,**args)}
        if intent in {"ram","cpu"}:
            self.tasks.update(task_id,"EXECUTING",detail="Reading OS metrics"); info=system_info(); return {"text":f"CPU {info.get('cpu_percent','n/a')}% | RAM {info.get('ram_percent','n/a')}%" if intent=="ram" else f"CPU {info.get('cpu_percent','n/a')}% | {info.get('cpu_count','n/a')} logical CPUs","intent":intent,"source":"OS API","data":info}
        if intent=="time":return {"text":system_info()["time"],"intent":intent,"source":"system clock"}
        if intent=="status":return {"text":"JARVIS is online. Use the SYSTEM panel for live subsystem health.","intent":intent,"source":"health checks","data":self.status()}
        if intent=="remember":
            content=text.split(None,1)[1] if len(text.split(None,1))>1 else ""; self.store.remember(content,kind="user_requested",importance=3); return {"text":"Memory stored.","intent":intent,"source":"SQLite"}
        if intent=="forget":
            q=text.split(None,1)[1] if len(text.split(None,1))>1 else ""; return {"text":f"Removed {self.store.forget(q)} matching memory record(s).","intent":intent,"source":"SQLite"}
        if intent=="python":
            m=re.search(r"([\w./\\-]+\.py)(?:\s+(.*))?$",text); script=m.group(1) if m else ""; d=self.perms.check("execute_python",script)
            if d.level!="SAFE":
                cid=self._confirmation("execute python",script,d.reason,lambda:self.pyexec.run_script(script,(m.group(2) or "").split() if m else [])); self.tasks.update(task_id,"WAITING_CONFIRMATION",detail="Waiting for Python execution approval"); return {"text":f"Confirmation required to execute {script}.","intent":intent,"permission":d.level,"confirmation_id":cid}
            r=self.pyexec.run_script(script,(m.group(2) or "").split() if m else []); return {"text":f"Started {r['script']} as PID {r['pid']}","intent":intent,"source":"PythonExecutionManager","task":r}
        if intent=="open_app":
            target=text.split(None,1)[1].strip(); return {"text":f"Launch requested for {target}.","intent":intent,"verification":open_application(target)}
        if intent=="list_tasks":
            tasks=self.pyexec.list(); return {"text":"\n".join(f"{x['script']} · {x['status']} · PID {x['pid']}" for x in tasks) or "No Python tasks running or recorded.","intent":intent,"tasks":tasks}
        if intent=="terminal":
            cmd=text.split(None,2)[-1] if len(text.split(None,2))>=3 else ""; d=self.perms.check("terminal",cmd)
            if d.level!="SAFE":
                cid=self._confirmation("run terminal",cmd,d.reason,lambda:self.terminal.run_line(cmd)); return {"text":"Confirmation required before running a terminal command.","intent":intent,"permission":d.level,"confirmation_id":cid}
            r=self.terminal.run_line(cmd); return {"text":r.stdout or r.stderr,"intent":intent,"source":"terminal","returncode":r.returncode,"stderr":r.stderr}
        if intent=="web":
            selected=self._selected_agent(intent,text)
            self.tasks.update(task_id,"EXECUTING",detail=f"Researching for {selected}")
            query=text
            if selected=="FactCheckAgent": query="Fact check this claim and compare independent sources: "+text
            elif selected=="NewsAgent": query="Find the latest reliable news and recent reporting about: "+text
            elif selected=="GitHubAgent": query="Research GitHub repositories, releases, issues and code references for: "+text
            r=self.researcher.research(query,self.ollama,self.router.route(text),self.cache)
            return {"text":r["text"],"intent":"web_research","source":"web research","sources":r["sources"],"research_agent":selected,"research_latency_ms":r["latency_ms"],"cache":r["cache"]}
        if self._selected_agent(intent,text)=="DocumentAgent":
            hits=self.rag.search(text,8) or self.store.search(text,8)
            if hits:
                return {"text":"DocumentAgent found relevant local content:\n"+"\n".join((h.get("content") or h.get("title") or "")[:900] for h in hits),"intent":"document","source":"local documents","hits":hits}
        if re.search(r"\b(project|documentation|docs|memory|what did i|remembered)\b",text,re.I):
            hits=self.rag.search(text,5) or self.store.search(text,5)
            if hits:return {"text":"Relevant local knowledge:\n"+"\n".join((h.get("content") or h.get("title") or "")[:700] for h in hits),"intent":"rag","source":"local knowledge","hits":hits}
        model=self.router.route(text); key=self.cache.key("llm",model,text.lower()); cached=self.cache.get(key)
        if cached:return {"text":cached["text"],"intent":intent,"model":model,"backend":cached.get("backend","cache"),"cache":"hit"}
        hits=self.store.search(text,4); messages=[{"role":"system","content":f"You are JARVIS, a precise local-first assistant. Model role: {self.router.classify(text)}. Never claim actions you did not perform. Be concise on low-memory systems."}]
        if hits:messages.append({"role":"system","content":"Relevant memory:\n"+"\n".join(h["content"] for h in hits)})
        messages.append({"role":"user","content":text}); self.tasks.update(task_id,"EXECUTING",detail=f"Calling {model}")
        r=self.ollama.chat(model,messages,False); answer=r.get("message",{}).get("content","") or "No response returned by the local model."
        self.cache.set(key,{"text":answer,"backend":r.get("_backend")},ttl=60,source=r.get("_backend","local_model"))
        if snapshot(self.s.ram_soft_limit_gb,self.s.ram_critical_limit_gb).get("mode")=="CRITICAL":self.cache.clear_temp(); self.ollama.unload_inactive(); low_ram_cleanup()
        return {"text":answer,"intent":intent,"model":model,"backend":r.get("_backend",self.ollama.backend),"latency_ms":r.get("_latency_ms"),"cache":"miss"}
    def stream_chat(self,text):
        intent=classify(text)
        if intent in {"ram","cpu","time","remember","forget","status","python","open_app","list_tasks","web"}:yield {"type":"final","data":self.chat(text)}; return
        model=self.router.route(text); messages=[{"role":"system","content":"You are JARVIS, a precise local-first assistant. Never claim actions you did not perform."},{"role":"user","content":text}]; self._emit("agent.state",state="SPEAKING",model=model)
        try:
            full=""
            for chunk in self.ollama.stream_chat(model,messages):
                piece=chunk.get("message",{}).get("content","")
                if piece:full+=piece; yield {"type":"delta","data":piece}
            yield {"type":"final","data":{"text":full,"intent":intent,"model":model,"backend":self.ollama.backend}}
        except Exception as exc:yield {"type":"final","data":{"text":f"Local model unavailable: {exc}","error":str(exc),"intent":intent,"model":model}}
