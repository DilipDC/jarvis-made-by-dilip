#!/usr/bin/env bash
set -euo pipefail
python -m uvicorn jarvis_app.core.app:app --host 127.0.0.1 --port 8000
