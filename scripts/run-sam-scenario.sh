#!/usr/bin/env bash
# Validate exported, normalized REAL SAM evidence. Never infer PASS from CLI exit.
set -euo pipefail
exec python3 "$(cd "$(dirname "$0")" && pwd)/check-sam-trace.py" "$@"
