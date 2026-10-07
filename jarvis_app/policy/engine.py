from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml
@dataclass(slots=True)
class PolicyDecision:
    level:str; reason:str; rule:str
class PolicyEngine:
    def __init__(self,path):self.path=Path(path); self.data={}; self._mtime=0.0; self.reload()
    def reload(self):
        try:self.data=yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}; self._mtime=self.path.stat().st_mtime
        except FileNotFoundError:self.data={"version":1,"defaults":{"confirmation":"confirm"},"actions":{}}; self._mtime=0.0
    def _refresh_if_changed(self):
        try:m=self.path.stat().st_mtime
        except FileNotFoundError:m=0.0
        if m!=self._mtime:self.reload()
    def evaluate(self,action,target=""):
        self._refresh_if_changed(); key=action.strip().lower().replace(" ","_"); rule=self.data.get("actions",{}).get(key) or self.data.get("actions",{}).get(action.lower()) or self.data.get("actions",{}).get("*") or {}
        mode=str(rule.get("mode",self.data.get("defaults",{}).get("confirmation","confirm"))).lower()
        if mode not in {"allow","confirm","deny"}:mode="confirm"
        allowed=rule.get("targets")
        if allowed and target and not any(str(target).startswith(str(x)) for x in allowed):return PolicyDecision("deny","Target is outside the policy allowlist.",key)
        return PolicyDecision(mode,str(rule.get("reason",f"Policy mode: {mode}")),key)
