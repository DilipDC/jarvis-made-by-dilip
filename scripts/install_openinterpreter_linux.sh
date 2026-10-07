#!/usr/bin/env bash
set -euo pipefail

echo "Installing the official Open Interpreter Linux CLI..."
curl -fsSL https://www.openinterpreter.com/install | sh

echo
echo "Verify with:"
echo "  interpreter --version"
echo
echo "JARVIS can then use Open Interpreter for approved Linux agent tasks."
