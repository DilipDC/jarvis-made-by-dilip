# Agent architecture

JARVIS includes PlannerAgent, ResearchAgent, CodingAgent, SystemAgent, MemoryAgent, RAGAgent, BrowserAgent, PythonAgent, ReviewerAgent and MemoryCompactorAgent.

Default limits are four agents, two parallel agents and depth two. The registry intentionally avoids unbounded recursive spawning.
