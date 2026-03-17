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
