from __future__ import annotations
import threading, time, uuid

class Scheduler:
    def __init__(self, store, events):
        self.store, self.events = store, events; self.items = {}; self.running = True
        for item in store.load_scheduled(): self.items[item['id']] = item
        self._thread = threading.Thread(target=self._loop, daemon=True, name='jarvis-scheduler'); self._thread.start()
    def add(self, delay_seconds, command):
        tid = str(uuid.uuid4()); task = {'id':tid,'due':time.time()+max(0,delay_seconds),'command':command,'status':'SCHEDULED'}
        self.items[tid] = task; self.store.save_scheduled(task); self.events.emit('scheduler.add', task=task); return task
    def cancel(self, task_id):
        task=self.items.get(task_id)
        if not task: return False
        task['status']='CANCELLED'; self.store.save_scheduled(task); self.events.emit('scheduler.cancel',task=task); return True
    def list(self): return sorted(self.items.values(), key=lambda x:x['due'])
    def stop(self): self.running=False
    def _loop(self):
        while self.running:
            now=time.time()
            for task in list(self.items.values()):
                if task['status']=='SCHEDULED' and task['due']<=now:
                    task['status']='DUE'; self.store.save_scheduled(task); self.events.emit('scheduler.due',task=task)
            time.sleep(0.5)
