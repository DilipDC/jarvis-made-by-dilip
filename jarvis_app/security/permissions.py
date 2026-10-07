from __future__ import annotations
from dataclasses import dataclass
from ..policy.engine import PolicyEngine
SAFE="SAFE"; CONFIRM="CONFIRM"; BLOCKED="BLOCKED"
@dataclass(slots=True)
class Decision:
    level:str; reason:str; rule:str=""
class PermissionManager:
    def __init__(self,policy:PolicyEngine|None=None):self.policy=policy
    def check(self,action,target=""):
        key=action.lower().replace(" ","_").replace("-","_")
        if key.startswith("execute_python"):key="execute_python"
        elif "terminal" in key:key="terminal"
        elif "delete" in key:key="delete_file"
        if self.policy:
            d=self.policy.evaluate(key,target); return Decision({"allow":SAFE,"confirm":CONFIRM,"deny":BLOCKED}.get(d.level,CONFIRM),d.reason,d.rule)
        return Decision(CONFIRM,"No policy engine configured; confirmation required.",key)
