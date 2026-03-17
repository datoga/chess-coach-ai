# Chess Coach AI

## Overview
AI chess coaching plugin for Claude Code with multi-agent cowork architecture.

## Agents
- **Intel** (`agents/intel.md`) — Player profiling, Lichess API, Opening Explorer
- **GM** (`agents/gm.md`) — Stockfish/Maia analysis, error classification, training roadmaps
- **Mind** (`agents/mind.md`) — Tilt detection, time patterns, psychological profiling
- **Biohack** (`agents/biohack.md`) — Nutrition, sleep, supplementation protocols

## Tools
All Python tools are in `tools/`. Run tests with `pytest tests/ -v`.

## Schemas
JSON schemas in `data/schemas/` define contracts between agents.

## Storage
Games stored in `vault/` (local) or Google Drive (primary). Never commit vault contents.

## Language
All code and docs in English. Agents respond in the user's language.

## Setup

### Prerequisites
- Python 3.12+ with `pip install -r requirements.txt`
- Stockfish 18+ (`brew install stockfish`)
- Node.js 24+ (for ChessAgine MCP: `npx -y chessagine-mcp`)
- Optional: lc0 for Maia models (`brew install lc0`)

### Verify Setup
```bash
pytest tests/ -v          # All tests should pass
stockfish <<< "uci"       # Should print Stockfish info
npx -y chessagine-mcp     # Should start MCP server
```

### Google Drive Setup (Optional)
1. Create a Google Cloud project
2. Enable Google Drive API
3. Download credentials.json to project root
4. Run the auth flow (first save_game with gdrive_enabled=True will prompt)
