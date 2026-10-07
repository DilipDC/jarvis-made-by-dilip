#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -x .venv/bin/python ]]; then ./scripts/install_linux.sh; fi
. .venv/bin/activate
python -m uvicorn jarvis_app.core.app:app --host 127.0.0.1 --port 8000 &
PID=$!
trap 'kill "$PID" 2>/dev/null || true' EXIT INT TERM
sleep 2
if command -v xdg-open >/dev/null 2>&1; then xdg-open http://127.0.0.1:8000 >/dev/null 2>&1 || true; fi
wait "$PID"
