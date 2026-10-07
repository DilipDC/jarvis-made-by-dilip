#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/install_linux.sh
./scripts/RUN_JARVIS.sh
