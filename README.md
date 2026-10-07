# JARVIS — BUILT BY DILIP

A lightweight, local-first, agentic computer assistant designed to feel like a personal JARVIS operating layer rather than a generic chatbot dashboard.

## Core

- Qwen3 0.6B for general work through Ollama.
- Qwen2.5-Coder 1.5B for coding tasks.
- Fast deterministic routing before LLM calls.
- SQLite memory and document RAG.
- TTL/LRU cache.
- Trusted Python subprocess execution and monitoring.
- Persistent scheduler.
- SAFE / CONFIRM / BLOCKED permission gates.
- Real-time WebSocket task/state events.
- Lightweight futuristic UI.
- Optional MCP, Playwright, voice, computer-control, semantic RAG and OpenAI Agents SDK integrations.

## Run

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1
pip install -e '.[test]'
python -m uvicorn jarvis_app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

## Ollama

Configure:

```env
GENERAL_MODEL=qwen3:0.6b
CODING_MODEL=qwen2.5-coder:1.5b
OLLAMA_URL=http://127.0.0.1:11434
LOW_RAM_MODE=true
```

## Optional OpenAI agent fallback

```bash
pip install -e '.[openai]'
```

Then set `OPENAI_ENABLED=true`, `OPENAI_API_KEY`, and optionally `OPENAI_MODEL`.

## Diagnostics

```bash
jarvis doctor
jarvis status
jarvis chat "What is my RAM usage?"
```

## Tests

```bash
pytest -q
```

The repository distinguishes WORKING, PARTIALLY WORKING, BLOCKED, NOT IMPLEMENTED and NOT TESTED features instead of claiming unsupported functionality.

See `docs/` for architecture, security, MCP, RAG, Python execution, browser, voice, Windows/Linux and performance details.
