#!/usr/bin/env bash
# Backward-compatible entry point; implementation uses Python's standard library.
set -euo pipefail
exec python3 "$(cd "$(dirname "$0")" && pwd)/probe.py" "$@"
