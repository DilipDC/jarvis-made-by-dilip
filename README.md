# JARVIS — BUILT BY DILIP

A lightweight, local-first, multi-agent AI operating layer for the computer.

## v0.3 upgrade

- AirLLM-first local inference with Qwen3 0.6B and Qwen2.5-Coder 1.5B.
- Lazy model loading and one-model-at-a-time discipline.
- Ten bounded agent roles with configurable concurrency/depth limits.
- Two-layer cache: bounded temp LRU + bounded SQLite persistent cache.
- Central YAML policy engine under `solution/restrictions.yaml`.
- Deterministic fast path before model calls.
- NORMAL / LOW / CRITICAL RAM telemetry and emergency cache cleanup.
- Existing memory, RAG, scheduler, Python execution, browser, MCP, voice and WebSocket subsystems preserved.

## Target machine

Default settings are tuned for constrained 2–4 GB systems. This is a resource target, not a universal guarantee: OS overhead, Python packages and model preparation can exceed the available RAM on a 2 GB machine.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[airllm,test]"
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -e ".[airllm,test]"
```

Start:

```bash
python -m uvicorn jarvis_app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

## Backend

AirLLM is preferred:

```env
MODEL_BACKEND=airllm
GENERAL_MODEL=Qwen/Qwen3-0.6B
CODING_MODEL=Qwen/Qwen2.5-Coder-1.5B
```

Set `MODEL_BACKEND=ollama` to force the lightweight Ollama fallback.

## Diagnostics

```bash
jarvis doctor
jarvis status
pytest -q
```

## Growth target

The code cannot guarantee 8,000 GitHub stars in one month. That outcome depends on product quality, documentation, distribution, contributors and community adoption. This release therefore optimizes for a strong open-source foundation rather than fabricated growth claims.

See `solution/` and `docs/` for customization and low-RAM architecture.
