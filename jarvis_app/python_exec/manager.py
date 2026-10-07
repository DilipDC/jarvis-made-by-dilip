from __future__ import annotations
import os, sys, uuid, subprocess, time, threading, pathlib, signal
from dataclasses import dataclass,asdict

@dataclass
class Task:
    task_id:str; script:str; pid:int|None; status:str; started_at:float; ended_at:float|None=None; stdout:str=''; stderr:str=''; exit_code:int|None=None; working_directory:str|None=None
class PythonExecutionManager:
    def __init__(self, trusted_paths:list[str], default_timeout=120, store=None): self.trusted=[pathlib.Path(p).resolve() for p in trusted_paths]; self.timeout=default_timeout; self.tasks={}; self.lock=threading.RLock(); self.store=store
    def _resolve(self, script):
        p=pathlib.Path(script).expanduser(); candidates=[p] if p.is_absolute() else [root/p for root in self.trusted]; matches=[]
        for c in candidates:
            try:
                rc=c.resolve(strict=True)
            except FileNotFoundError: continue
            if rc.is_file() and rc.suffix.lower()=='.py' and any(root==rc or root in rc.parents for root in self.trusted): matches.append(rc)
        unique=list(dict.fromkeys(matches))
        if len(unique)!=1: raise FileNotFoundError(f'expected one trusted Python script, found {len(unique)}')
        return unique[0]
    def run_script(self, script, arguments=None, working_directory=None, timeout=None):
        p=self._resolve(script); args=arguments or []; wd=pathlib.Path(working_directory or p.parent).resolve()
        if not any(root==wd or root in wd.parents for root in self.trusted): raise PermissionError('working directory outside trusted paths')
        task_id=str(uuid.uuid4()); proc=subprocess.Popen([sys.executable,'-u',str(p),*map(str,args)],cwd=wd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=(os.name!='nt'))
        task=Task(task_id,p.name,proc.pid,'RUNNING',time.time(),working_directory=str(wd)); self.tasks[task_id]=task
        if self.store: self.store.save_python_task(asdict(task))
        def watch():
            try:
                out,err=proc.communicate(timeout=timeout or self.timeout); task.stdout=out[-12000:]; task.stderr=err[-12000:]; task.exit_code=proc.returncode; task.status='COMPLETED' if proc.returncode==0 else 'FAILED'
            except subprocess.TimeoutExpired:
                self._terminate_process(proc); out,err=proc.communicate(); task.stdout=out[-12000:]; task.stderr=err[-12000:]; task.exit_code=None; task.status='TIMEOUT'
            task.ended_at=time.time()
            if self.store: self.store.save_python_task(asdict(task))
        threading.Thread(target=watch,daemon=True).start(); return asdict(task)
    def _terminate_process(self, proc):
        try:
            if os.name!='nt': os.killpg(proc.pid, signal.SIGTERM)
            else: proc.terminate()
        except Exception: proc.kill()
    def stop(self, task_id):
        t=self.tasks[task_id];
        if t.pid and t.status=='RUNNING':
            try:
                if os.name!='nt': os.killpg(t.pid, signal.SIGTERM)
                else: subprocess.run(['taskkill','/PID',str(t.pid),'/T','/F'],capture_output=True)
            except Exception: pass
            t.status='CANCELLED'; t.ended_at=time.time()
            if self.store: self.store.save_python_task(asdict(t))
        return asdict(t)
    def list(self): return [asdict(x) for x in self.tasks.values()]
