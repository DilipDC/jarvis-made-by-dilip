# JARVIS — BUILT BY DILIP

> A lightweight, local-first, multi-agent AI assistant built for real computers, including low-RAM machines.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/) [![AirLLM](https://img.shields.io/badge/Inference-AirLLM-orange)](https://github.com/lyz-code/airllm) [![Ubuntu](https://img.shields.io/badge/Linux-Ubuntu-orange?logo=ubuntu)](https://ubuntu.com/) [![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?logo=windows)](https://www.microsoft.com/windows)

## What is JARVIS?

JARVIS is an experimental personal AI operating layer by DILIPDC. It combines local LLM inference, specialist agents, internet research, memory, RAG, Python execution, browser tooling, system information, scheduling and optional voice/computer/MCP integrations behind one orchestrator.

The central design goal is simple: useful AI should not require a high-end PC.

## What it does

- **Local AI:** AirLLM-first inference with Qwen3 0.6B for general tasks and Qwen2.5-Coder 1.5B for coding.
- **WebResearchAgent:** searches public web sources, fetches readable pages, extracts useful text, asks the local model to synthesize evidence and returns numbered sources.
- **FactCheckAgent:** routes verification requests through multi-source research.
- **NewsAgent:** handles recent/current news requests.
- **DocumentAgent:** works with local documents and the existing RAG layer.
- **GitHubAgent:** researches repositories, issues, releases, commits and code.
- **CodingAgent:** code explanation, debugging, refactoring and implementation.
- **SystemAgent:** CPU/RAM/platform information and approved local system operations.
- **MemoryAgent:** explicit persistent memory operations.
- **RAGAgent:** retrieves relevant local knowledge.
- **BrowserAgent:** optional browser workflows.
- **PythonAgent:** trusted Python execution with the existing permission system.
- **ReviewerAgent:** reviews assumptions and results.
- **MemoryCompactorAgent:** reduces stale temporary state.

## How the request flows

```text
User
  ↓
JARVIS Core / Orchestrator
  ↓
Intent + Agent Router
  ├─ WebResearchAgent → search → fetch → extract → local LLM → cited answer
  ├─ FactCheckAgent  → independent sources → comparison
  ├─ NewsAgent       → recent web research
  ├─ GitHubAgent     → repository/code research
  ├─ DocumentAgent   → local RAG
  ├─ CodingAgent     → coding model
  ├─ PythonAgent     → trusted execution
  └─ SystemAgent     → local OS APIs
```

## Low-RAM architecture

JARVIS is designed around a **2–4 GB RAM target profile**. It uses small models, lazy loading, idle unloading, bounded agents, bounded parallelism, short web contexts, temporary LRU caching, persistent SQLite caching and RAM-pressure cleanup.

Recommended profile:

```text
General model: Qwen3 0.6B
Coding model:  Qwen2.5-Coder 1.5B
Agents:        bounded
Context:       short
Cache:         bounded
Browser/voice:  optional
```

Actual speed and memory usage depend on CPU, RAM, storage, OS, model cache and optional components.

## Installation — Windows 10/11

```powershell
git clone https://github.com/DilipDC/jarvis-made-by-dilip.git
cd jarvis-made-by-dilip
scripts\SETUP_AND_RUN_WINDOWS.bat
```

Or separately:

```text
scripts\install_windows.bat
scripts\RUN_JARVIS.bat
```

The repository also contains an Inno Setup definition and a GitHub Actions workflow that builds a reproducible Windows EXE/installer.

## Installation — Ubuntu/Linux

```bash
git clone https://github.com/DilipDC/jarvis-made-by-dilip.git
cd jarvis-made-by-dilip
chmod +x scripts/*.sh
./scripts/SETUP_AND_RUN_LINUX.sh
```

Or:

```bash
./scripts/install_linux.sh
./scripts/RUN_JARVIS.sh
```

JARVIS runs locally at `http://127.0.0.1:8000`.

## Developer setup

```bash
python -m venv .venv
# Linux: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e ".[airllm,test]"
python -m compileall -q jarvis_app launcher.py
pytest -q
```

## Web research examples

```text
Search the internet and explain how AirLLM works.
Research the latest developments in local LLM inference.
Fact check this claim: ...
Research the best open-source Python agent frameworks on GitHub.
```

The research pipeline is intentionally lighter than a full autonomous browser stack: it searches, retrieves selected public pages, limits extracted text, synthesizes locally and caches results.

## Safety

Information operations such as web search, RAG retrieval and system information are designed as safe operations. Actions such as Python execution and terminal commands remain behind the existing permission/confirmation architecture.

Do not run commands or scripts you do not understand.

## Compatibility

| Platform | Status |
|---|---|
| Windows 11 | Primary |
| Windows 10 | Primary |
| Ubuntu/Linux | Primary |
| Windows 8/8.1 | Legacy |
| Windows 7 | Legacy |
| 2–4 GB RAM | Target profile |

Windows 7/8 are documented as legacy targets rather than a false full-stack guarantee. Current Ollama for Windows requires Windows 10 or later, and modern AirLLM/PyTorch combinations cannot responsibly be guaranteed on Win7/8.

## Project structure

```text
jarvis-made-by-dilip/
├── jarvis_app/
│   ├── agent/       # core orchestration
│   ├── agents/      # specialist agents
│   ├── cache/       # LRU + SQLite cache
│   ├── models/      # model routing + AirLLM
│   ├── rag/         # local retrieval
│   ├── tasks/       # task lifecycle
│   ├── tools/       # tool registry
│   └── web/         # internet research
├── scripts/         # Windows/Linux setup and run
├── installer/       # Windows installer definition
├── tests/
├── docs/
├── launcher.py
└── pyproject.toml
```

## Open-source architecture references

JARVIS was designed after studying proven patterns from open-source projects such as Browser Use for browser-agent orchestration, LlamaIndex for routing/RAG workflows, and Microsoft MarkItDown for document-processing ideas. These are architectural references; JARVIS does not copy their source code.

## About DILIPDC

**DILIPDC** is the creator of JARVIS. The project reflects DILIP's interest in practical software and hardware engineering across Python, C++, Java, embedded systems, ESP32/microcontrollers, robotics, AI/ML, local LLMs, cybersecurity research, Linux, Windows and automation.

> Built by DILIP. Designed to be modified. Designed to run locally.

## Roadmap direction

```text
Local LLM + Agent Router
        +
Web Research + Fact Checking
        +
Memory + RAG
        +
Python + Browser + Computer Tools
        +
Voice + Hardware / IoT
        ↓
Local AI operating layer
```

## Discoverability keywords

`AI assistant`, `personal AI`, `local AI`, `local LLM`, `offline AI`, `multi-agent AI`, `AI agents`, `Python AI`, `AirLLM`, `Qwen`, `Qwen3`, `Qwen2.5-Coder`, `low RAM AI`, `4GB RAM AI`, `lightweight AI`, `RAG`, `web research`, `AI web search`, `fact checking AI`, `GitHub agent`, `coding agent`, `browser agent`, `Python agent`, `AI automation`, `Jarvis AI`, `Linux AI`, `Ubuntu AI`, `Windows AI`, `open source AI`, `embedded AI`, `robotics AI`

## Voice-first desktop mode

The web UI now follows a simple voice-assistant design: a central animated purple JARVIS orb, microphone button, spoken responses, compact system cards and a mobile-friendly conversation view.

Example voice commands:

    Who created you?
    What can you do?
    Search the internet for the latest AI news.
    Remember that my project deadline is Friday.
    Open Chrome.
    Run command terminal: ...
    Click 500 300.
    Type hello world.
    Press enter.
    Hotkey ctrl+alt+t.
    Take a screenshot.

Browser speech recognition is used when supported. Browser speech synthesis reads JARVIS responses aloud. Optional Python voice packages remain available for a native voice backend.

## Desktop control

JARVIS supports an **approved-action desktop layer** on Windows and Linux. The desktop controller uses PyAutoGUI when installed and can perform bounded actions such as mouse movement/clicks, typing, key presses, hotkeys and screenshots.

Desktop actions are not treated as unrestricted shell access. The agent routes them through the permission/confirmation layer. Terminal commands remain separately protected.

Install the optional desktop backend:

    python -m pip install -e ".[computer]"


## Hybrid RAG

JARVIS keeps SQLite FTS as the low-RAM retrieval baseline and supports optional semantic reranking with `sentence-transformers` and `all-MiniLM-L6-v2`. This gives a practical hybrid path: lexical retrieval stays cheap, while semantic reranking is enabled only when requested.

Enable it with:

    JARVIS_SEMANTIC_RAG=1

Install the optional RAG extra:

    python -m pip install -e ".[rag]"

Leave semantic RAG disabled on a very small machine when RAM is more important than retrieval quality.
## MCP: two ready integrations

JARVIS now includes two lazy-loaded MCP integrations based on the official MCP server ecosystem:

1. **Filesystem MCP** — file read/write/search operations restricted to the JARVIS working directory and marked CONFIRM.
2. **Memory MCP** — knowledge-graph memory server, marked SAFE.

MCP servers are **lazy**: JARVIS does not launch them at startup. They start only when inspected or used, which helps the 2–4 GB RAM target.

Install the optional MCP client:

    python -m pip install -e ".[mcp]"

The default configuration is in `config/mcp.json`.

The application exposes:

    GET  /api/mcp
    POST /api/mcp/filesystem/inspect
    POST /api/mcp/memory/inspect

MCP uses the standard client/server protocol rather than embedding a separate custom plugin format.

## Permanent JARVIS identity

JARVIS has a persistent identity profile stored in its local SQLite database during startup. It knows its project identity, creator and core capabilities.

Examples:

    Who are you?
    Who created you?
    What can you do?
    About yourself.

Identity information is kept separate from temporary LLM response caching, so it does not expire when the normal cache is cleared.
## Support the project

If JARVIS is useful, **star the repository**, fork it, report bugs, propose agents, improve documentation or submit pull requests. Stars are useful because they improve project discovery, but no repository can honestly guarantee a particular star count.

## JARVIS — BUILT BY DILIP

**Local. Modular. Low-RAM. Agentic. Extensible.**