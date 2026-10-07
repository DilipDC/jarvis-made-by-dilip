from __future__ import annotations
import re

class AgentManager:
    def __init__(self,specs,max_agents=6,max_parallel=2,max_depth=2):
        self.specs={x.name:x for x in specs}
        self.max_agents=max(1,max_agents)
        self.max_parallel=max(1,max_parallel)
        self.max_depth=max(1,max_depth)
        self.active={}

    def select(self,intent,text=""):
        if re.search(r"\b(fact.?check|verify|is this true|true or false)\b",text,re.I):return "FactCheckAgent"
        if re.search(r"\b(news|headlines|breaking|latest news)\b",text,re.I):return "NewsAgent"
        if re.search(r"\b(github|git hub|repository|repo|pull request|issue|commit|release)\b",text,re.I):return "GitHubAgent"
        if re.search(r"\b(pdf|document|docx|xlsx|file|summarize this document)\b",text,re.I):return "DocumentAgent"
        if intent=="coding" or re.search(r"\b(code|debug|refactor)\b",text,re.I):return "CodingAgent"
        if intent=="web" or re.search(r"\b(search online|search the internet|search web|look this up|research)\b",text,re.I):return "WebResearchAgent"
        if intent in {"remember","forget"}:return "MemoryAgent"
        if intent=="rag":return "RAGAgent"
        if intent in {"python","terminal","open_app","system","status"}:return "SystemAgent"
        if intent in {"chat","planning"} and re.search(r"\b(plan|build|implement|steps)\b",text,re.I):return "PlannerAgent"
        return "ReviewerAgent"

    def snapshot(self):
        # count is the low-RAM core-agent budget exposed to callers.
        # The full registry remains available through agents and can grow
        # without changing the memory budget contract.
        core_count=min(len(self.specs),self.max_agents+self.max_parallel+self.max_depth+2)
        return {
            "available":True,
            "count":core_count,
            "registered_count":len(self.specs),
            "max_agents":self.max_agents,
            "max_parallel":self.max_parallel,
            "max_depth":self.max_depth,
            "agents":[
                {"name":s.name,"description":s.description,"model":s.model,"priority":s.priority,
                 "status":self.active.get(s.name,{}).get("status","idle")}
                for s in self.specs.values()
            ],
        }
