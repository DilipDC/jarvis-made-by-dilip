# Troubleshooting

### JARVIS starts but says Ollama is OFFLINE
Start Ollama and confirm `http://127.0.0.1:11434/api/tags` responds. Pull the configured models before asking JARVIS to use local generation.

### MCP is WARN/OFFLINE
Install the optional MCP dependency. Configure a trusted server explicitly; arbitrary servers are not trusted by default.

### Browser automation is unavailable
Install the optional Playwright dependency and the required browser runtime.

### Python execution says script not found
Place the script under one of the configured trusted directories and avoid ambiguous duplicate names.

### A terminal action asks for confirmation
This is intentional. External side effects are not silently executed.
