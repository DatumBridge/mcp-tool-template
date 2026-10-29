#!/bin/sh
# Language-neutral Weaver MCP contract check. The server may use any language.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
exec python3 "$ROOT/scripts/check_contract.py" "$@"
