# JARVIS — BUILT BY DILIP

> Lightweight, local-first, multi-agent AI assistant for real computers and low-RAM systems.

## What is working

- **Local AI:** AirLLM-first with Ollama fallback.
- **Multi-agent routing:** WebResearch, News, FactCheck, GitHub, Document/RAG, Coding, Python, Memory, Browser and System agents.
- **Persistent memory:** SQLite-backed explicit memories.
- **Reminders:** natural phrases such as `Remind me at 8 PM to write homework`, `remember this: write homework at 8 PM`, and `remind me in 30 minutes` create persistent scheduler entries. When due, the UI shows a notification, plays a short sound and speaks the reminder.
- **Browser search:** `Open browser and search for laptop` opens the installed browser with a URL-encoded Google search.
- **Current web research:** current/news/price questions use web retrieval and source citations instead of pretending the local model knows live values.
- **MCP:** official Python SDK ClientSession/stdio transport is used; filesystem and memory servers are lazy-loaded and permission-aware.
- **Low RAM:** bounded context, bounded cache, lazy loading and idle cleanup.
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
