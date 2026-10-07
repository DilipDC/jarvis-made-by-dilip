# JARVIS — BUILT BY DILIP

> Lightweight, local-first, multi-agent AI assistant for real computers and low-RAM systems.

## What is working

- **Local AI:** AirLLM-first with Ollama fallback.
- **Multi-agent routing:** WebResearch, News, FactCheck, GitHub, Document/RAG, Coding, Python, Memory, Browser and System agents.
- **Persistent memory:** SQLite-backed explicit memories.
- **Reminders:** natural phrases such as `Remind me at 8 PM to write homework`, `remember this: write homework at 8 PM`, and `remind me in 30 minutes` create persistent scheduler entries. When due, the UI shows a notification, plays a short sound and speaks the reminder.
- **Browser search:** `Open Firefox
Take a screenshot
Control my computer and open Firefox
Open browser and search for laptop
Use my computer to open Firefox and inspect the page` opens the installed browser with a URL-encoded Google search.
- **Current web research:** current/news/price questions use web retrieval and source citations instead of pretending the local model knows live values.
- **MCP:** official Python SDK ClientSession/stdio transport is used; filesystem and memory servers are lazy-loaded and permission-aware.
- **Low RAM:** bounded context, bounded cache, lazy loading and idle cleanup.
- **Desktop control:** Native PyAutoGUI actions plus optional Linux computer autopilot through Open Interpreter.
- **Agent safety:** bounded action-loop guard, sandboxed Open Interpreter execution and the existing permission/confirmation system.
- **Desktop helpers:** `happy.py` and an authorized, bounded Nmap diagnostic helper.

## Kali/Linux setup

```bash
cd /home/student/Desktop/jarvis-made-by-dilip
source .venv/bin/activate
git pull
python -m pip install -e .
python launcher.py
```

Optional features:

```bash
python -m pip install -e ".[computer]"
python -m pip install -e ".[mcp]"
bash scripts/install_openinterpreter_linux.sh
```

For MCP servers, Node.js/npm/npx must also be available because the configured servers use stdio launchers.

## Desktop helper files

Create them on your Desktop:

```bash
python scripts/create_desktop_tools.py
```

This creates:

```text
~/Desktop/happy.py
~/Desktop/nmap_scan.py
```

Run the smoke test:

```bash
python ~/Desktop/happy.py
```

Run the Nmap diagnostic against an authorized target:

```bash
python ~/Desktop/nmap_scan.py 192.168.1.0/24
```

The Nmap helper uses only `nmap -sV --top-ports 100 TARGET`.

## Example commands

```text
Who are you?
Open browser and search for laptop
Search the web for the current Jio stock price
What is the latest AI news?
Remember this: write homework at 8 PM
Remind me at 8 PM to write homework
Remind me in 30 minutes to check my project
Run scripts/happy.py
Run scripts/nmap_scan.py 192.168.1.0/24
```

## Accuracy

JARVIS only reports a completed action when the corresponding subsystem returns success. Current web answers include retrieved sources and should report uncertainty when sources disagree or cannot be read. Browser launch and desktop actions return verification data rather than unconditional success claims.

## Safety

Terminal, Python execution and desktop-control actions remain behind the existing permission/confirmation architecture. Nmap is provided as a bounded diagnostic wrapper and should only be used on networks you own or are explicitly authorized to test.

## Architecture

```text
User
 ↓
Intent Router
 ↓
Specialist Agent
 ↓
Tool
 ↓
Verified Result
```

The web UI receives live scheduler and agent events over WebSocket.

## Computer autopilot integrations

JARVIS uses its own permissioned desktop manager for deterministic actions and can optionally delegate broader Linux tasks to the official Open Interpreter CLI. The Open Interpreter bridge uses an explicit sandbox, on-request approval and a bounded loop guard; JARVIS does not bundle or silently bypass its safety controls. Open Interpreter documents Linux/native-app computer-use support through its QA tooling.

The computer-autopilot workflow is inspired by the observe -> act -> verify pattern used by general desktop agents such as ACE. ACE itself is a commercial product and no public code/API was available for a direct code transplant, so this repository does not claim to embed ACE code.

OpenJarvis contributed architectural reference points for tool-executor separation and loop-guarded agent execution. JARVIS keeps those ideas lightweight and Python-native instead of importing the larger OpenJarvis runtime. OpenJarvis is Apache-2.0 licensed.

Install the Linux bridge:

```bash
bash scripts/install_openinterpreter_linux.sh
interpreter --version
```

Then start JARVIS and try:

```text
Control my computer and open Firefox
Use my computer to open Firefox and search for Python tutorials
```

