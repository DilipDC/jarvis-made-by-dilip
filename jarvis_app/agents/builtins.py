from __future__ import annotations
from .base import AgentSpec
from .manager import AgentManager
def build_agent_manager(general_model,coding_model,max_agents=4,max_parallel=2,max_depth=2):
    specs=[
        AgentSpec("PlannerAgent","Decompose multi-step requests.",("planning",),general_model,90),
        AgentSpec("ResearchAgent","Retrieve current web/documentation information.",("research","web"),general_model,70),
        AgentSpec("CodingAgent","Inspect, patch, test, and explain code.",("coding",),coding_model,95),
        AgentSpec("SystemAgent","Read system metrics and manage approved local actions.",("system",),general_model,75),
        AgentSpec("MemoryAgent","Retrieve and manage explicit user memories.",("memory",),general_model,60),
        AgentSpec("RAGAgent","Retrieve relevant local document chunks.",("rag",),general_model,65),
        AgentSpec("BrowserAgent","Perform approved browser workflows.",("browser",),general_model,55),
        AgentSpec("PythonAgent","Discover and execute trusted Python scripts.",("python",),coding_model,80),
        AgentSpec("ReviewerAgent","Review actions and detect incorrect assumptions.",("review",),general_model,100),
        AgentSpec("MemoryCompactorAgent","Compact stale temporary/session state.",("maintenance",),general_model,20),
    ]
    return AgentManager(specs,max_agents,max_parallel,max_depth)
