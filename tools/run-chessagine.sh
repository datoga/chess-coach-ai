#!/bin/bash
# Wrapper to launch ChessAgine MCP with proper path resolution
CHESSAGINE_PATH="${CHESSAGINE_PATH:-$HOME/.local/lib/chessagine-mcp}"
exec node "$CHESSAGINE_PATH/build/runner/stdio.js"
