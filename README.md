# Chess Coach AI

AI-powered chess coaching system built as a **Claude Code plugin** with a multi-agent cowork architecture.

## Features

- **Intel Agent** — Player profiling, Lichess API integration, Opening Explorer analysis, opponent scouting
- **GM Agent** — Stockfish/Maia analysis, error classification by cognitive origin, personalized training roadmaps, auto-analysis with training insights
- **Mind Agent** — Tilt detection, time pattern analysis, psychological profiling, session readiness assessment
- **Biohack Agent** — Evidence-based nutrition protocols, supplementation, sleep optimization, pre-game routines

## Quick Start

### Prerequisites

```bash
# Required
brew install stockfish          # Stockfish 18+
node --version                  # Node.js 24+ (for ChessAgine MCP)
python3 --version               # Python 3.12+

# Optional
brew install lc0                # For Maia models
```

### Install

```bash
# Clone the repo
git clone https://github.com/datoga/chess-coach-ai.git
cd chess-coach-ai

# Install Python dependencies
pip install -r requirements.txt

# Verify ChessAgine MCP
npx -y chessagine-mcp --help
```

### Use as Claude Code Plugin

```bash
# Load the plugin
claude --plugin-dir ./chess-coach-ai

# Or install globally
claude plugin install ./chess-coach-ai
```

### Available via the `/chess-coach-ai:coach` skill

Once loaded, the coach skill is available in any Claude Code session. Example commands:

- `Prepare my game against [lichess username]`
- `Review this game: [paste PGN]`
- `Create a training plan`
- `Intel on [lichess username]`
- `Save this game: [paste PGN]`
- `Import my games from lichess`
- `Starting a training session — slept 6 hours, energy 7/10`

## Architecture

```
User → /chess-coach-ai:coach (Coordinator)
       ├→ Intel (Lichess API, Opening Explorer, chessdb.cn)
       ├→ GM (Stockfish, Maia2, PGN analysis, training insights)
       ├→ Mind (time patterns, tilt detection, resilience)
       └→ Biohack (nutrition, sleep, supplements, protocols)
       → Coordinator synthesizes → Unified response
```

The coordinator dispatches agents via **cowork** (Claude Code agent teams). Agents communicate through JSON contracts defined in `data/schemas/`.

## Storage

Games are stored in the **Game Vault**:
- **Primary:** Google Drive (requires OAuth2 setup)
- **Fallback:** Local `vault/` directory

Supports: manual PGN paste, Lichess URL import, bulk game download.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific tool tests
pytest tests/test_pgn_parser.py -v
pytest tests/test_dqm_calculator.py -v
```

## Evals

Trigger evals (does the right agent activate?) and quality evals (is the output correct?) are in:
- `skills/coach/eval-set.json` + `skills/coach/evals/evals.json`
- `evals/{intel,gm,mind,biohack}/`

## Project Structure

```
├── agents/           # Agent definitions (Intel, GM, Mind, Biohack)
├── skills/coach/     # Coordinator skill
├── tools/            # Python tools (Lichess client, PGN parser, etc.)
├── data/
│   ├── schemas/      # JSON Schema contracts between agents
│   ├── openings/     # lichess-org/chess-openings dataset
│   ├── supplements.json
│   └── nutrition_protocols.json
├── templates/        # Output templates (dossiers, reviews, roadmaps)
├── evals/            # Agent-level trigger + quality evals
├── hooks/            # Quality gate hooks
├── vault/            # Local game storage (gitignored)
└── tests/            # pytest test suite
```

## License

MIT
