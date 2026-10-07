# JARVIS — BUILT BY DILIP

> A lightweight, local-first, multi-agent AI assistant built for real computers, including low-RAM machines.

## Core capabilities

- Local AI with AirLLM-first and Ollama fallback.
- Multi-agent routing for web research, news, fact checking, GitHub, documents, coding, Python, memory, system tasks and browser workflows.
- Persistent SQLite memory and explicit reminders.
- Real browser search: **"open browser and search for laptop"** launches the installed browser with a URL-encoded search query.
- Current-information research: questions such as **"What is Jio's stock price now?"** are routed to web research and returned with retrieved sources rather than stale local memory.
- Live scheduler events with browser notification, sound and speech when a reminder becomes due.
- Low-RAM architecture with bounded context, cache and lazy optional components.
- Approved desktop control and confirmation gates for OS actions.
- Optional MCP integrations and RAG.

## Quick start — Linux/Kali

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python launcher.py
```

Optional desktop controller:

```bash
python -m pip install -e ".[computer]"
```

MCP:

```bash
python -m pip install -e ".[mcp]"
```

MCP configuration is in `config/mcp.json`. Filesystem MCP is CONFIRM-protected; memory MCP is SAFE. MCP servers are lazy-loaded and do not silently receive unrestricted OS access.

## Useful commands

```text
Open browser and search for laptop
Search the web for the current Jio stock price
What is the latest AI news?
Remember that I need to finish homework
Remind me at 8 PM to write homework
Remind me in 30 minutes to check my project
Run scripts/happy.py
Run scripts/nmap_scan.py 192.168.1.0/24
```

The Nmap helper is deliberately bounded to `-sV --top-ports 100`. Use it only on systems/networks you own or are authorized to test.

## Create the helper files on your Desktop

```bash
python scripts/create_desktop_tools.py
```

This creates:

```text
Desktop/
├── happy.py
└── nmap_scan.py
```

## Architecture

```text
User
 ↓
Intent router
 ↓
Specialist agent
 ↓
Verified tool/result
 ├─ WebResearchAgent → search → fetch → synthesize → citations
 ├─ NewsAgent → recent multi-source research
 ├─ FactCheckAgent → independent-source comparison
 ├─ GitHubAgent → GitHub research
 ├─ Document/RAGAgent → local documents
 ├─ CodingAgent → coding model
 ├─ PythonAgent → trusted scripts
 ├─ BrowserAgent → browser workflows
 ├─ MemoryAgent → persistent memory
 └─ SystemAgent → approved OS operations
```

The UI receives scheduler and agent events over WebSocket so reminders are visible immediately instead of only being stored as backend events.

## Accuracy model

JARVIS does not claim that a browser was opened, a script executed, or a reminder fired unless the corresponding subsystem reports success. Current web facts are sourced from retrieved public pages; if sources disagree or cannot be retrieved, JARVIS reports the uncertainty instead of inventing a value.

## Project

Created by **DILIPDC**. Built to be modified, tested and run locally.
