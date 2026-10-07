from __future__ import annotations
import re
class AgentManager:
    def __init__(self,specs,max_agents=4,max_parallel=2,max_depth=2):
        self.specs={x.name:x for x in specs}; self.max_agents=max_agents; self.max_parallel=max_parallel; self.max_depth=max_depth; self.active={}
    def select(self,intent,text=""):
        if intent=="coding" or re.search(r"\b(code|debug|refactor|repository)\b",text,re.I):return "CodingAgent"
        if intent=="web":return "ResearchAgent"
        if intent in {"remember","forget"}:return "MemoryAgent"
        if intent=="rag":return "RAGAgent"
        if intent in {"python","terminal","open_app","system","status"}:return "SystemAgent"
        if intent in {"chat","planning"} and re.search(r"\b(plan|build|implement|steps)\b",text,re.I):return "PlannerAgent"
        return "ReviewerAgent"
    def snapshot(self):
        return {"available":True,"count":len(self.specs),"max_agents":self.max_agents,"max_parallel":self.max_parallel,"max_depth":self.max_depth,
                "agents":[{"name":s.name,"description":s.description,"model":s.model,"priority":s.priority,"status":self.active.get(s.name,{}).get("status","idle")} for s in self.specs.values()]}
