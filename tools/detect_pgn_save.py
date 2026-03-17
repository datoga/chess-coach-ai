#!/usr/bin/env python3
"""Hook script: detect when a PGN file is written to the vault."""
import json
import sys
from pathlib import Path


def main():
    """Read hook input from stdin, check if written file is a vault PGN."""
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = hook_input.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    path = Path(file_path)
    if path.suffix != ".pgn" or "vault" not in path.parts:
        sys.exit(0)

    # Validate PGN content
    if path.exists():
        content = path.read_text()
        # Basic PGN validation: must contain at least a result tag and moves
        if "[Result" not in content:
            print(f"WARNING: Invalid PGN written to vault: {file_path}", file=sys.stderr)
            sys.exit(2)  # Block — invalid PGN

    sys.exit(0)


if __name__ == "__main__":
    main()
