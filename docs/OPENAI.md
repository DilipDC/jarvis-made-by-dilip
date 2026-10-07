# OpenAI Integration

JARVIS is local-first. Ollama/Qwen remains the default path.

An optional `openai-agents` adapter can be enabled with `OPENAI_ENABLED=true` and `OPENAI_API_KEY`. The adapter uses the OpenAI Agents SDK for an advanced-agent fallback. The code does not require the package or a key for normal local operation.

Suggested model settings can be controlled with `OPENAI_MODEL`; the current default is `gpt-5.6-luna`.
