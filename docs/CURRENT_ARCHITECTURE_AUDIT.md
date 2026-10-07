# Current architecture audit

The original repository contained useful agent, memory, RAG, scheduling, Python execution, UI and WebSocket layers, but its runtime imports referenced missing `models`, `cache` and OpenAI adapter modules.

This upgrade repairs those gaps and adds AirLLM-first inference, bounded agents, low-RAM resource controls, central policy and cache observability.

A full end-to-end 2 GB benchmark is not claimed because the target hardware is not available in this execution environment.
