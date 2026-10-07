# Open-source architecture research

JARVIS was compared with mature open-source projects before the 1.0 design pass.

## Browser Use
Browser Use is a large open-source browser-agent project. Its public architecture shows a useful pattern: isolate browser work as a subagent so the main orchestrator receives a task result rather than carrying every browser action in its own state.

JARVIS keeps its existing browser subsystem and adds WebResearchAgent as a lighter HTTP research path. Browser automation remains optional because a full browser stack is expensive on 2–4 GB machines.

## LlamaIndex
LlamaIndex documents routing, RAG, agent workflows and multi-agent orchestration. JARVIS follows the same broad idea of routing a request to a specialized worker while keeping its own small manager and SQLite/RAG implementation.

## Microsoft MarkItDown
MarkItDown demonstrates a practical document-to-Markdown pipeline. JARVIS keeps document processing optional and lightweight rather than making the large dependency mandatory.

No source files were copied from these projects.
