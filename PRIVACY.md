# Privacy Policy — Chess Coach AI

**Last updated:** 2026-03-17

## Overview

Chess Coach AI is an open-source Claude Code plugin that runs entirely on your local machine. Your data stays with you.

## Data Collection

**We do not collect, store, transmit, or share any user data.** Period.

This includes:
- Chess games (PGN files)
- Game analysis results
- Player profiles and scouting reports
- Training roadmaps and progress data
- Wellness and biohacking data (sleep, nutrition, energy levels)
- Lichess usernames or any platform credentials
- Any personal information

## How Data is Processed

- All analysis runs locally on your machine (Stockfish, Python tools)
- Games are stored in your local `vault/` directory only
- The plugin queries public APIs (Lichess, chessdb.cn) to fetch **publicly available** game data — it does not send your personal data to these services
- Lichess API calls use only public endpoints that require no authentication for read access

## Third-Party Services

The plugin interacts with these external services for **read-only public data**:

| Service | What is accessed | Data sent |
|---------|-----------------|-----------|
| Lichess API | Public player profiles and games | Player username (public) |
| chessdb.cn | Position evaluations | Chess positions (FEN strings, no personal data) |
| Lichess Tablebase API | Endgame evaluations | Chess positions (FEN strings, no personal data) |

No personal data, credentials, or private information is ever transmitted to these services.

## Local Storage

All data created by the plugin is stored locally:
- `vault/` — Your saved games, analysis results, and training state
- All files remain on your machine under your control
- Nothing is uploaded, synced, or shared unless you explicitly do so

## Open Source

This plugin is fully open source (MIT License). You can inspect every line of code at:
https://github.com/datoga/chess-coach-ai

## Contact

For privacy questions: open an issue at https://github.com/datoga/chess-coach-ai/issues
