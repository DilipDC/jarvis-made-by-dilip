# JARVIS — BUILT BY DILIP

Final 1.0.0 direction: lightweight local-first multi-agent AI operating layer.

New specialist agents:
- WebResearchAgent — searches the public internet, reads multiple sources, synthesizes an answer and cites sources.
- FactCheckAgent — cross-checks claims.
- NewsAgent — handles current/recent news.
- DocumentAgent — handles document-oriented tasks.
- GitHubAgent — researches public repositories, issues, releases and code.

Core:
- AirLLM-first Qwen3 0.6B / Qwen2.5-Coder 1.5B.
- Lazy model loading and idle unloading.
- Bounded agents, two-layer cache and RAM pressure cleanup.
- Central policy engine.
- Existing RAG, memory, Python, browser, MCP, voice and scheduler systems retained.

Windows 10/11:
Run scripts\SETUP_AND_RUN_WINDOWS.bat.

Ubuntu/Linux:
chmod +x scripts/*.sh
./scripts/SETUP_AND_RUN_LINUX.sh

Windows installer:
The GitHub Actions workflow builds JARVIS-Setup.exe from launcher.py and installer/JARVIS.iss.

Important compatibility note:
Windows 7/8 are legacy targets only. Current Ollama for Windows requires Windows 10 or later, and modern AirLLM/PyTorch combinations are not a safe Win7/8 guarantee. The installer does not falsely claim that those systems can run every AI backend.

2–4 GB RAM:
The default low-RAM profile uses the 0.6B general model, short context, bounded agents and aggressive cache limits. Actual performance depends on hardware and OS.
