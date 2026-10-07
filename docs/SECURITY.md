# Security

Permission levels: SAFE, CONFIRM, BLOCKED.

Sensitive actions should request confirmation before mutation. High-risk prohibited categories are blocked. Python scripts must resolve under configured trusted paths. Terminal argv execution uses `shell=False`. Output buffers are bounded. Secrets are excluded from logs and `.gitignore` excludes `.env`, caches, databases, virtual environments and model files.
