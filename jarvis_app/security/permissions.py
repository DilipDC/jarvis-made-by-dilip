from __future__ import annotations
from dataclasses import dataclass
SAFE='SAFE'; CONFIRM='CONFIRM'; BLOCKED='BLOCKED'
@dataclass
class Decision: level:str; reason:str
class PermissionManager:
    def check(self, action:str, target:str=''):
        a=action.lower()
        if any(x in a for x in ['credential theft','disable firewall','stealth persistence','backdoor','bypass security','dump passwords','token theft']): return Decision(BLOCKED,'High-risk or prohibited action')
        if any(x in a for x in ['delete','shutdown','reboot','kill','firewall','send message','modify security','run terminal','terminal command','write file']): return Decision(CONFIRM,'High-impact or external side-effect action requires explicit confirmation')
        return Decision(SAFE,'Low-risk action')
