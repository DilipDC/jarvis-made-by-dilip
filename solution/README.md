# JARVIS solution layer

This directory is the user-customizable control plane.

- `restrictions.yaml` controls allow/confirm/deny behavior.
- `prompts/` can hold prompt templates.
- `workflows/` can hold workflows.
- `agents/` can hold custom definitions.

Keep user customization here instead of hard-coding it into Python source.
