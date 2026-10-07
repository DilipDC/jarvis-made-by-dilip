from __future__ import annotations
from dataclasses import dataclass
from ..policy.engine import PolicyEngine

SAFE="SAFE"; CONFIRM="CONFIRM"; BLOCKED="BLOCKED"

@dataclass(slots=True)
class Decision:
    level:str
    reason:str
    rule:str=""

class PermissionManager:
    """Small, deterministic permission gate for local JARVIS actions."""
    def __init__(self,policy:PolicyEngine|None=None):
        self.policy=policy

    @staticmethod
    def _key(action):
        key=str(action).strip().lower().replace(" ","_").replace("-","_")
        if key.startswith("execute_python"): return "execute_python"
        if "terminal" in key or key.startswith("run_command"): return "terminal"
        if "disable_firewall" in key or "turn_off_firewall" in key: return "disable_firewall"
        if "delete" in key: return "delete_file"
        if key.startswith(("open_","launch_")) or key in {"open_browser","open_chrome","open_firefox","open_edge"}:
            return "browser"
        return key

    def check(self,action,target=""):
        key=self._key(action)

        # Explicit safety invariants remain enforced even when a policy file is absent.
        if key=="disable_firewall":
            return Decision(BLOCKED,"Firewall disabling is blocked by default.","disable_firewall")
        if key=="browser":
            return Decision(SAFE,"Opening a browser/application is a safe local action.","browser")

        if self.policy:
            d=self.policy.evaluate(key,target)
            return Decision({"allow":SAFE,"confirm":CONFIRM,"deny":BLOCKED}.get(d.level,CONFIRM),d.reason,d.rule)

        if key in {"read_file","system_info","remember"}:
            return Decision(SAFE,"Safe local action.",key)
        if key in {"delete_file","write_file","execute_python","terminal","forget"}:
            return Decision(CONFIRM,"Confirmation required for this action.",key)
        return Decision(CONFIRM,"No policy rule configured; confirmation required.",key)
