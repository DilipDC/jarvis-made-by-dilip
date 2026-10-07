from __future__ import annotations
import hashlib
import json
from collections import deque

class LoopGuard:
    """Bounded action-loop guard inspired by OpenJarvis-style agent execution."""

    def __init__(self,max_steps=8,max_repeats=2,history_size=12):
        self.max_steps=max(1,int(max_steps))
        self.max_repeats=max(1,int(max_repeats))
        self.history=deque(maxlen=max(1,int(history_size)))
        self.steps=0

    @staticmethod
    def fingerprint(action,payload=None):
        body=json.dumps({"action":action,"payload":payload or {}},sort_keys=True,default=str)
        return hashlib.sha256(body.encode()).hexdigest()[:16]

    def allow(self,action,payload=None):
        if self.steps>=self.max_steps:
            return False,"maximum agent steps reached"
        fp=self.fingerprint(action,payload)
        repeats=sum(1 for x in self.history if x==fp)
        if repeats>=self.max_repeats:
            return False,"repeated action loop detected"
        self.history.append(fp)
        self.steps+=1
        return True,"allowed"

    def reset(self):
        self.history.clear()
        self.steps=0

    def snapshot(self):
        return {"steps":self.steps,"max_steps":self.max_steps,
                "max_repeats":self.max_repeats,"history_size":len(self.history)}
