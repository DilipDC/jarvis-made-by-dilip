# Low-RAM mode

JARVIS uses a constrained local profile:
- AirLLM-first inference.
- One primary model loaded at a time.
- Lazy loading and idle unload.
- Short context/generation limits.
- Bounded agents and caches.
- Deterministic system APIs before LLM calls.

AirLLM currently documents `AutoModel.from_pretrained(...)` with Hugging Face model IDs and layer-wise inference. Runtime feasibility still depends on the operating system, CPU/GPU and available RAM.
