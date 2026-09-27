#!/usr/bin/env bash
# Claude Code Pre-Tool-Use Hook: Block Destructive Commands Wrapper

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_EXEC="python3"

if ! command -v python3 &> /dev/null; then
    PYTHON_EXEC="python"
fi

# Execute Python hook passing all stdin or arguments
exec "$PYTHON_EXEC" "$SCRIPT_DIR/block_destructive.py" "$@"
