# JARVIS Architecture

JARVIS is a local-first agent runtime with a thin HTTP/WebSocket UI. The runtime path is:

`UI → Fast Intent → Cache/Memory/RAG → deterministic tool → local model → optional cloud fallback → verification → event stream`

Core layers:

- `agent/`: routing, task lifecycle, confirmations and response generation.
- `tools/`: explicit capability registry and metadata.
- `memory/`: SQLite WAL storage for memories, tasks, documents, audit events and tool runs.
- `rag/`: lightweight document ingestion plus FTS retrieval.
- `models/`: Ollama local model client/router and optional OpenAI Agents SDK adapter.
- `events/`: real-time event bus exposed through WebSocket.
- `tasks/`: persistent task state machine.
- `python_exec/`: isolated subprocess execution for trusted Python files.
- `scheduler/`: persistent scheduled-task store with recovery on restart.
- `security/`: centralized SAFE / CONFIRM / BLOCKED decisions.

The design intentionally keeps heavyweight vision, browser, voice, MCP and cloud components optional.
