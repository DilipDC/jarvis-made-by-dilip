# JARVIS 1.0.0

Added:
- WebResearchAgent: public internet search, multi-source retrieval, local-model synthesis and numbered citations.
- FactCheckAgent, NewsAgent, DocumentAgent and GitHubAgent.
- Windows one-click setup/run scripts and reproducible EXE/installer workflow.
- Linux setup/run scripts.
- AirLLM 4.x dependency alignment.

Open-source references:
- Browser Use for mature browser-agent orchestration.
- LlamaIndex for routing, RAG and multi-agent workflow patterns.
- Microsoft MarkItDown for document-to-Markdown design ideas.

These projects were used as architectural references; their source was not copied.

Compatibility:
- Windows 10/11 and Ubuntu are primary full-stack targets.
- Windows 7/8 are legacy compatibility targets. Current Ollama for Windows requires Windows 10+, so Ollama cannot be promised on Windows 7/8.
- AirLLM uses modern PyTorch/Transformers, so full AirLLM support on Win7/8 is not claimed.
- 2–4 GB RAM is a target profile, not a universal performance guarantee.
