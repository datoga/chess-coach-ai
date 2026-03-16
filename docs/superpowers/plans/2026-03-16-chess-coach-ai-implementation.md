# Chess Coach AI — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code plugin with 4 specialized agents (Intel, GM, Mind, Biohack) that provide AI-powered chess coaching via cowork teams.

**Architecture:** Claude Code plugin with coordinator skill dispatching to specialized agents. Python tools for data processing (Lichess API, Stockfish, PGN analysis). Google Drive storage with local fallback. ChessAgine MCP for engine analysis.

**Tech Stack:** Python 3.12+, python-chess, berserk (Lichess API), stockfish wrapper, ChessAgine MCP, Google Drive API, pytest

**Spec:** `docs/superpowers/specs/2026-03-16-chess-coach-ai-design.md`

---

## Chunk 1: Project Scaffolding & Core Infrastructure

### Task 1: Project setup, dependencies, and plugin manifest

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.mcp.json`
- Create: `requirements.txt`
- Create: `CLAUDE.md`
- Create: `.gitignore`
- Create: `vault/.gitkeep`

- [ ] **Step 1: Create plugin manifest**

```json
// .claude-plugin/plugin.json
{
  "name": "chess-coach-ai",
  "description": "AI-powered chess coaching system with multi-agent architecture. Integrates technical analysis, biohacking, and applied psychometrics to treat chess players as cognitive athletes.",
  "version": "0.1.0",
  "author": { "name": "datoga" },
  "license": "MIT",
  "keywords": ["chess", "coaching", "lichess", "stockfish", "biohacking", "training"]
}
```

- [ ] **Step 2: Create MCP configuration**

```json
// .mcp.json
{
  "mcpServers": {
    "chessagine": {
      "command": "npx",
      "args": ["-y", "chessagine-mcp"]
    }
  }
}
```

- [ ] **Step 3: Create requirements.txt**

```
chess>=1.11.0
stockfish>=3.28.0
berserk>=0.13.0
cairosvg>=2.7.0
google-api-python-client>=2.0.0
google-auth-oauthlib>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
responses>=0.25.0
```

- [ ] **Step 4: Create .gitignore**

```
__pycache__/
*.pyc
.pytest_cache/
vault/my-games/
vault/opponents/
vault/insights/
vault/index.json
vault/roadmap_state.json
*.egg-info/
dist/
build/
.env
credentials.json
token.json
```

- [ ] **Step 5: Create CLAUDE.md**

```markdown
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
```

- [ ] **Step 6: Create vault/.gitkeep**

- [ ] **Step 7: Install dependencies**

Run: `cd /Users/datoga/hack/chess-coach-ai && pip install -r requirements.txt`

- [ ] **Step 8: Commit**

```bash
git add .claude-plugin/ .mcp.json requirements.txt CLAUDE.md .gitignore vault/
git commit -m "feat: project scaffolding — plugin manifest, MCP config, dependencies"
```

---

### Task 2: JSON schemas for agent contracts

**Files:**
- Create: `data/schemas/player_report.json`
- Create: `data/schemas/game_analysis.json`
- Create: `data/schemas/training_insights.json`
- Create: `data/schemas/mental_profile.json`
- Create: `data/schemas/biohack_protocol.json`
- Create: `data/schemas/roadmap_state.json`
- Create: `data/schemas/game_vault_entry.json`

- [ ] **Step 1: Create player_report.json schema**

See spec Section 3 for the full schema. Define as JSON Schema draft-07 with required fields: `username`, `platform`, `ratings`, `style_archetype`, `style_sub_profile`.

- [ ] **Step 2: Create game_analysis.json schema**

See spec Section 4. Required: `game_id`, `user_color`, `result`, `acpl`, `dqm`, `critical_moments`.

- [ ] **Step 3: Create training_insights.json schema**

See spec Section 4. Required: `training_insights.game_id`, `training_insights.insights`, `training_insights.roadmap_update`. Ensure `suggested_block_rebalance` keys match canonical phase_balance keys: `openings`, `middlegame`, `endgame`, `tactics`.

- [ ] **Step 4: Create mental_profile.json schema**

See spec Section 5. Required: `tilt_detected`, `tilt_type`, `session_recommendation`.

- [ ] **Step 5: Create biohack_protocol.json schema**

See spec Section 6. Required: `current_state`, `competition_phase`, `training_intensity_modifier`.

- [ ] **Step 6: Create roadmap_state.json schema**

See spec Section 8. Required: `user_profile`, `phase_balance`, `active_weaknesses`. Validate that `phase_balance` uses canonical keys only.

- [ ] **Step 7: Create game_vault_entry.json schema**

See spec Section 7. Required: `game_id`, `source`, `category`, `pgn_file`, `sync_status`.

- [ ] **Step 8: Create validate_schema.py tool**

```python
# tools/validate_schema.py
"""Validates JSON data against schemas in data/schemas/."""
import json
import sys
from pathlib import Path

SCHEMA_DIR = Path(__file__).parent.parent / "data" / "schemas"

def validate(data: dict, schema_name: str) -> list[str]:
    """Validate data against a named schema. Returns list of errors (empty = valid)."""
    schema_path = SCHEMA_DIR / f"{schema_name}.json"
    if not schema_path.exists():
        return [f"Schema not found: {schema_name}"]
    schema = json.loads(schema_path.read_text())
    errors = []
    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"Missing required field: {field}")
    return errors

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: validate_schema.py <schema_name> <json_file>")
        sys.exit(1)
    schema_name = sys.argv[1]
    json_file = sys.argv[2]
    data = json.loads(Path(json_file).read_text())
    errors = validate(data, schema_name)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print("Valid")
```

- [ ] **Step 9: Write test for validate_schema**

```python
# tests/test_validate_schema.py
from tools.validate_schema import validate

def test_valid_player_report():
    data = {"username": "test", "platform": "lichess", "ratings": {}, "style_archetype": "activist", "style_sub_profile": "balanced"}
    errors = validate(data, "player_report")
    assert errors == []

def test_missing_required_field():
    data = {"username": "test"}
    errors = validate(data, "player_report")
    assert len(errors) > 0
    assert any("platform" in e for e in errors)
```

- [ ] **Step 10: Run tests**

Run: `cd /Users/datoga/hack/chess-coach-ai && python -m pytest tests/test_validate_schema.py -v`

- [ ] **Step 11: Commit**

```bash
git add data/schemas/ tools/validate_schema.py tests/test_validate_schema.py
git commit -m "feat: JSON schemas for agent contracts + validation tool"
```

---

### Task 3: PGN parser tool

**Files:**
- Create: `tools/pgn_parser.py`
- Create: `tests/test_pgn_parser.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_pgn_parser.py
import chess.pgn
from tools.pgn_parser import parse_pgn, extract_moves_with_clocks, get_game_phases

SAMPLE_PGN = """[Event "Rated Blitz game"]
[White "player1"]
[Black "player2"]
[Result "1-0"]
[WhiteElo "1500"]
[BlackElo "1450"]
[ECO "B01"]
[TimeControl "300+0"]

1. e4 {[%clk 0:04:58]} d5 {[%clk 0:04:55]} 2. exd5 {[%clk 0:04:50]} Qxd5 {[%clk 0:04:48]} 3. Nc3 {[%clk 0:04:45]} Qa5 {[%clk 0:04:40]} 1-0"""

def test_parse_pgn_returns_game():
    game = parse_pgn(SAMPLE_PGN)
    assert game is not None
    assert game.headers["White"] == "player1"
    assert game.headers["Result"] == "1-0"

def test_parse_pgn_invalid():
    result = parse_pgn("not a pgn")
    assert result is None

def test_extract_moves_with_clocks():
    game = parse_pgn(SAMPLE_PGN)
    moves = extract_moves_with_clocks(game)
    assert len(moves) == 6
    assert moves[0]["move"] == "e4"
    assert moves[0]["clock_seconds"] is not None

def test_get_game_phases():
    game = parse_pgn(SAMPLE_PGN)
    phases = get_game_phases(game)
    assert "opening" in phases
    assert "middlegame" in phases
    assert "endgame" in phases
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_pgn_parser.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement pgn_parser.py**

```python
# tools/pgn_parser.py
"""Parse PGN games into structured data with clock times and game phases."""
import io
import re
import chess.pgn


def parse_pgn(pgn_text: str) -> chess.pgn.Game | None:
    """Parse a PGN string into a python-chess Game object."""
    try:
        game = chess.pgn.read_game(io.StringIO(pgn_text))
        return game
    except Exception:
        return None


def extract_moves_with_clocks(game: chess.pgn.Game) -> list[dict]:
    """Extract moves with clock times from a parsed game."""
    moves = []
    node = game
    move_num = 0
    while node.variations:
        next_node = node.variation(0)
        move_num += 1
        clock = _extract_clock(next_node.comment)
        moves.append({
            "move_number": (move_num + 1) // 2,
            "color": "white" if move_num % 2 == 1 else "black",
            "move": next_node.move.uci(),
            "san": node.board().san(next_node.move),
            "clock_seconds": clock,
            "fen_after": next_node.board().fen(),
            "comment": next_node.comment,
        })
        node = next_node
    return moves


def get_game_phases(game: chess.pgn.Game) -> dict[str, list[dict]]:
    """Split game moves into opening (1-15), middlegame (16-35), endgame (36+)."""
    all_moves = extract_moves_with_clocks(game)
    return {
        "opening": [m for m in all_moves if m["move_number"] <= 15],
        "middlegame": [m for m in all_moves if 16 <= m["move_number"] <= 35],
        "endgame": [m for m in all_moves if m["move_number"] > 35],
    }


def _extract_clock(comment: str) -> float | None:
    """Extract clock time in seconds from a PGN comment like [%clk 0:04:58]."""
    match = re.search(r'\[%clk (\d+):(\d+):(\d+(?:\.\d+)?)\]', comment)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    return None
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_pgn_parser.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add tools/pgn_parser.py tests/test_pgn_parser.py
git commit -m "feat: PGN parser with clock extraction and game phase splitting"
```

---

### Task 4: Opening classifier tool

**Files:**
- Create: `tools/opening_classifier.py`
- Create: `tests/test_opening_classifier.py`
- Create: `data/openings/` (download lichess-org/chess-openings)

- [ ] **Step 1: Download opening data**

Run: `cd /Users/datoga/hack/chess-coach-ai && mkdir -p data/openings && curl -sL https://raw.githubusercontent.com/lichess-org/chess-openings/master/a.tsv -o data/openings/a.tsv && curl -sL https://raw.githubusercontent.com/lichess-org/chess-openings/master/b.tsv -o data/openings/b.tsv && curl -sL https://raw.githubusercontent.com/lichess-org/chess-openings/master/c.tsv -o data/openings/c.tsv && curl -sL https://raw.githubusercontent.com/lichess-org/chess-openings/master/d.tsv -o data/openings/d.tsv && curl -sL https://raw.githubusercontent.com/lichess-org/chess-openings/master/e.tsv -o data/openings/e.tsv`

- [ ] **Step 2: Write failing tests**

```python
# tests/test_opening_classifier.py
from tools.opening_classifier import classify_opening, load_openings_db

def test_load_openings_db():
    db = load_openings_db()
    assert len(db) > 100

def test_classify_sicilian():
    result = classify_opening("1. e4 c5")
    assert result["eco"].startswith("B")
    assert "Sicilian" in result["name"]

def test_classify_unknown():
    result = classify_opening("1. a4 a5 2. b4")
    assert result["eco"] == "A00" or result["name"] == "Unknown"
```

- [ ] **Step 3: Implement opening_classifier.py**

```python
# tools/opening_classifier.py
"""Classify chess openings by ECO code using lichess-org/chess-openings data."""
import csv
from pathlib import Path
from functools import lru_cache

import chess
import chess.pgn
import io

OPENINGS_DIR = Path(__file__).parent.parent / "data" / "openings"


@lru_cache(maxsize=1)
def load_openings_db() -> list[dict]:
    """Load all opening TSV files into a list sorted by move count (longest first)."""
    openings = []
    for tsv_file in sorted(OPENINGS_DIR.glob("*.tsv")):
        with open(tsv_file, "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                moves = row.get("pgn", "").strip()
                openings.append({
                    "eco": row.get("eco", ""),
                    "name": row.get("name", ""),
                    "pgn": moves,
                    "move_count": len(moves.split()) if moves else 0,
                })
    openings.sort(key=lambda x: x["move_count"], reverse=True)
    return openings


def classify_opening(pgn_moves: str) -> dict:
    """Classify an opening from a PGN move string. Returns {eco, name, pgn}."""
    db = load_openings_db()
    # Normalize: parse moves to get board positions
    try:
        game = chess.pgn.read_game(io.StringIO(pgn_moves))
        if game is None:
            return {"eco": "A00", "name": "Unknown", "pgn": ""}
        board = game.board()
        positions = [board.fen()]
        for move in game.mainline_moves():
            board.push(move)
            positions.append(board.fen())
    except Exception:
        return {"eco": "A00", "name": "Unknown", "pgn": ""}

    # Match longest opening sequence
    for opening in db:
        try:
            op_game = chess.pgn.read_game(io.StringIO(opening["pgn"]))
            if op_game is None:
                continue
            op_board = op_game.board()
            op_positions = [op_board.fen()]
            for move in op_game.mainline_moves():
                op_board.push(move)
                op_positions.append(op_board.fen())
            if len(op_positions) <= len(positions):
                if all(op_positions[i] == positions[i] for i in range(len(op_positions))):
                    return {"eco": opening["eco"], "name": opening["name"], "pgn": opening["pgn"]}
        except Exception:
            continue

    return {"eco": "A00", "name": "Unknown", "pgn": ""}
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_opening_classifier.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add tools/opening_classifier.py tests/test_opening_classifier.py data/openings/
git commit -m "feat: opening classifier using lichess-org/chess-openings dataset"
```

---

### Task 5: Lichess API client

**Files:**
- Create: `tools/lichess_client.py`
- Create: `tests/test_lichess_client.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_lichess_client.py
import pytest
from unittest.mock import MagicMock, patch
from tools.lichess_client import LichessClient

@pytest.fixture
def client():
    return LichessClient()

def test_get_profile(client):
    with patch.object(client, '_client') as mock:
        mock.users.get_public_data.return_value = {
            "id": "testuser", "username": "TestUser",
            "perfs": {"blitz": {"rating": 1500}, "rapid": {"rating": 1600}}
        }
        profile = client.get_profile("testuser")
        assert profile["username"] == "TestUser"
        assert "ratings" in profile

def test_get_recent_games(client):
    with patch.object(client, '_client') as mock:
        mock.games.export_by_player.return_value = iter([
            {"id": "game1", "moves": "e4 e5", "players": {}}
        ])
        games = client.get_recent_games("testuser", max_games=1)
        assert len(games) == 1

def test_get_opening_explorer(client):
    with patch.object(client, '_request_explorer') as mock:
        mock.return_value = {
            "moves": [{"uci": "e2e4", "san": "e4", "white": 100, "draws": 50, "black": 50}]
        }
        result = client.get_opening_explorer("testuser", color="white")
        assert len(result["moves"]) > 0
```

- [ ] **Step 2: Implement lichess_client.py**

```python
# tools/lichess_client.py
"""Lichess API client using berserk library."""
import berserk
import requests
from typing import Optional


class LichessClient:
    """Wrapper around berserk for Lichess API access."""

    def __init__(self, token: Optional[str] = None):
        session = berserk.TokenSession(token) if token else None
        self._client = berserk.Client(session)

    def get_profile(self, username: str) -> dict:
        """Get player profile with ratings."""
        data = self._client.users.get_public_data(username)
        perfs = data.get("perfs", {})
        return {
            "username": data.get("username", username),
            "platform": "lichess",
            "ratings": {
                tc: perfs.get(tc, {}).get("rating", 0)
                for tc in ["bullet", "blitz", "rapid", "classical"]
            },
            "title": data.get("title"),
            "online": data.get("online", False),
            "last_seen": data.get("seenAt"),
        }

    def get_recent_games(self, username: str, max_games: int = 50,
                         time_control: Optional[str] = None) -> list[dict]:
        """Export recent games for a player."""
        kwargs = {"max": max_games, "clocks": True, "evals": True, "opening": True}
        if time_control:
            kwargs["perf_type"] = time_control
        games = list(self._client.games.export_by_player(username, **kwargs))
        return games

    def get_opening_explorer(self, username: str, color: str = "white",
                              speeds: Optional[list[str]] = None) -> dict:
        """Query the Lichess Opening Explorer for a specific player."""
        params = {"player": username, "color": color}
        if speeds:
            params["speeds"] = ",".join(speeds)
        return self._request_explorer(params)

    def _request_explorer(self, params: dict) -> dict:
        """Raw request to Lichess Opening Explorer API."""
        url = "https://explorer.lichess.ovh/player"
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_lichess_client.py -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add tools/lichess_client.py tests/test_lichess_client.py
git commit -m "feat: Lichess API client with profile, games, and opening explorer"
```

---

### Task 6: ChessDB cloud eval client

**Files:**
- Create: `tools/chessdb_client.py`
- Create: `tests/test_chessdb_client.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_chessdb_client.py
from unittest.mock import patch, MagicMock
from tools.chessdb_client import ChessDBClient

def test_query_position():
    client = ChessDBClient()
    with patch("tools.chessdb_client.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"status": "ok", "moves": [
                {"uci": "e2e4", "score": 30, "rank": 0}
            ]}
        )
        result = client.query_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        assert result["status"] == "ok"
        assert len(result["moves"]) > 0

def test_get_best_move():
    client = ChessDBClient()
    with patch("tools.chessdb_client.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            text="bestmove:e2e4"
        )
        move = client.get_best_move("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        assert move == "e2e4"

def test_fallback_on_timeout():
    client = ChessDBClient()
    with patch("tools.chessdb_client.requests.get", side_effect=Exception("timeout")):
        result = client.query_position("some_fen")
        assert result is None
```

- [ ] **Step 2: Implement chessdb_client.py**

```python
# tools/chessdb_client.py
"""Client for chessdb.cn cloud evaluation API."""
import requests
from typing import Optional

BASE_URL = "http://www.chessdb.cn/cdb.php"


class ChessDBClient:
    """Query the Chess Cloud Database for position evaluations."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def query_position(self, fen: str) -> Optional[dict]:
        """Get all known moves for a position."""
        try:
            resp = requests.get(
                BASE_URL,
                params={"action": "queryall", "board": fen, "json": 1},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def get_best_move(self, fen: str) -> Optional[str]:
        """Get the best move for a position."""
        try:
            resp = requests.get(
                BASE_URL,
                params={"action": "querybest", "board": fen},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            text = resp.text.strip()
            if text.startswith("bestmove:"):
                return text.split(":")[1].strip()
            return None
        except Exception:
            return None
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_chessdb_client.py -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add tools/chessdb_client.py tests/test_chessdb_client.py
git commit -m "feat: chessdb.cn cloud eval client with fallback handling"
```

---

### Task 7: Game Vault (local storage + Google Drive interface)

**Files:**
- Create: `tools/game_vault.py`
- Create: `tests/test_game_vault.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_game_vault.py
import json
import tempfile
from pathlib import Path
from tools.game_vault import GameVault

SAMPLE_PGN = '[White "p1"]\n[Black "p2"]\n[Result "1-0"]\n\n1. e4 e5 1-0'

def test_save_my_game(tmp_path):
    vault = GameVault(local_path=tmp_path)
    entry = vault.save_game(SAMPLE_PGN, category="my_game")
    assert entry["category"] == "my_game"
    assert (tmp_path / "my-games" / entry["pgn_file"]).exists()

def test_save_opponent_game(tmp_path):
    vault = GameVault(local_path=tmp_path)
    entry = vault.save_game(SAMPLE_PGN, category="opponent_prep", opponent="magnus")
    assert entry["category"] == "opponent_prep"
    assert "magnus" in entry["pgn_file"]

def test_index_updated(tmp_path):
    vault = GameVault(local_path=tmp_path)
    vault.save_game(SAMPLE_PGN, category="my_game")
    index = json.loads((tmp_path / "index.json").read_text())
    assert len(index) == 1

def test_list_games(tmp_path):
    vault = GameVault(local_path=tmp_path)
    vault.save_game(SAMPLE_PGN, category="my_game")
    vault.save_game(SAMPLE_PGN, category="my_game")
    games = vault.list_games()
    assert len(games) == 2

def test_google_drive_fallback(tmp_path):
    vault = GameVault(local_path=tmp_path, gdrive_enabled=True)
    # Without credentials, should fallback to local
    entry = vault.save_game(SAMPLE_PGN, category="my_game")
    assert entry["sync_status"] == "local_only"
```

- [ ] **Step 2: Implement game_vault.py**

```python
# tools/game_vault.py
"""Game vault: local PGN storage with Google Drive interface."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from tools.pgn_parser import parse_pgn
from tools.opening_classifier import classify_opening


class GameVault:
    """Store and retrieve PGN games with metadata."""

    def __init__(self, local_path: Optional[Path] = None, gdrive_enabled: bool = False):
        self.local_path = local_path or Path(__file__).parent.parent / "vault"
        self.gdrive_enabled = gdrive_enabled
        self._ensure_dirs()

    def save_game(self, pgn_text: str, category: str = "my_game",
                  opponent: Optional[str] = None) -> dict:
        """Save a PGN game to the vault. Returns vault entry dict."""
        game = parse_pgn(pgn_text)
        game_id = hashlib.sha256(pgn_text.encode()).hexdigest()[:16]
        now = datetime.now(timezone.utc).isoformat()

        # Classify opening
        opening = {"eco": "A00", "name": "Unknown"}
        if game:
            moves_str = " ".join(
                game.board().san(m) for m in list(game.mainline_moves())[:15]
            )
            opening = classify_opening(f"1. {moves_str}" if moves_str else "")

        # Determine file path
        if category == "opponent_prep" and opponent:
            subdir = self.local_path / "opponents" / opponent
            subdir.mkdir(parents=True, exist_ok=True)
            filename = f"{game_id}.pgn"
            pgn_rel_path = f"opponents/{opponent}/{filename}"
        else:
            subdir = self.local_path / "my-games"
            subdir.mkdir(parents=True, exist_ok=True)
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_str}_{game_id}.pgn"
            pgn_rel_path = f"my-games/{filename}"

        # Write PGN
        (subdir / filename).write_text(pgn_text)

        # Build entry
        entry = {
            "game_id": game_id,
            "source": "manual",
            "category": category,
            "opponent_username": opponent,
            "date_played": game.headers.get("Date", now) if game else now,
            "date_stored": now,
            "time_control": game.headers.get("TimeControl", "unknown") if game else "unknown",
            "result": game.headers.get("Result", "*") if game else "*",
            "user_color": "unknown",
            "opening_eco": opening["eco"],
            "opening_name": opening["name"],
            "tags": [],
            "pgn_file": pgn_rel_path,
            "insights_file": None,
            "auto_analyzed": False,
            "sync_status": "local_only",
        }

        # Update index
        self._update_index(entry)

        # Try Google Drive
        if self.gdrive_enabled:
            try:
                self._sync_to_gdrive(entry, pgn_text)
                entry["sync_status"] = "synced"
            except Exception:
                entry["sync_status"] = "local_only"

        return entry

    def list_games(self, category: Optional[str] = None) -> list[dict]:
        """List all games in the vault."""
        index = self._load_index()
        if category:
            return [e for e in index if e["category"] == category]
        return index

    def _ensure_dirs(self):
        for d in ["my-games", "opponents", "insights"]:
            (self.local_path / d).mkdir(parents=True, exist_ok=True)

    def _load_index(self) -> list[dict]:
        index_path = self.local_path / "index.json"
        if index_path.exists():
            return json.loads(index_path.read_text())
        return []

    def _update_index(self, entry: dict):
        index = self._load_index()
        index.append(entry)
        (self.local_path / "index.json").write_text(
            json.dumps(index, indent=2)
        )

    def _sync_to_gdrive(self, entry: dict, pgn_text: str):
        """Sync to Google Drive. Raises NotImplementedError until OAuth is configured."""
        raise NotImplementedError(
            "Google Drive sync requires OAuth2 credentials. "
            "Set up credentials.json and run the auth flow. "
            "See docs for setup instructions."
        )
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_game_vault.py -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add tools/game_vault.py tests/test_game_vault.py
git commit -m "feat: Game Vault with local storage and Google Drive fallback"
```

---

## Chunk 2: Analysis Tools (DQM, Time Analysis, Style & Error Classifiers)

### Task 8: DQM calculator

**Files:**
- Create: `tools/dqm_calculator.py`
- Create: `tests/test_dqm_calculator.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_dqm_calculator.py
from tools.dqm_calculator import calculate_dqm, calculate_acpl, MAX_ACPL_BY_LEVEL

def test_perfect_play():
    eval_diffs = [0, 0, 0, 0, 0]
    dqm = calculate_dqm(eval_diffs, rating=1500)
    assert dqm == 1.0

def test_terrible_play():
    eval_diffs = [200, 300, 250, 400, 500]
    dqm = calculate_dqm(eval_diffs, rating=1500)
    assert dqm < 0.2

def test_acpl():
    eval_diffs = [10, 20, 30, 40, 50]
    acpl = calculate_acpl(eval_diffs)
    assert acpl == 30.0

def test_dqm_level_relative():
    eval_diffs = [50, 50, 50]
    dqm_1200 = calculate_dqm(eval_diffs, rating=1200)
    dqm_2000 = calculate_dqm(eval_diffs, rating=2000)
    # Same ACPL but DQM should be worse for higher-rated player
    assert dqm_1200 > dqm_2000

def test_max_acpl_levels():
    assert MAX_ACPL_BY_LEVEL[1000] > MAX_ACPL_BY_LEVEL[2000]
```

- [ ] **Step 2: Implement dqm_calculator.py**

```python
# tools/dqm_calculator.py
"""Decision Quality Metric — normalized, level-relative quality score."""

# Calibrated max expected ACPL per rating band
MAX_ACPL_BY_LEVEL = {
    800: 200, 1000: 150, 1200: 120, 1400: 95,
    1500: 85, 1600: 75, 1800: 60, 2000: 45,
    2200: 35, 2400: 25, 2600: 18, 2800: 12,
}


def _get_max_acpl(rating: int) -> float:
    """Get max expected ACPL for a rating, interpolating between bands."""
    levels = sorted(MAX_ACPL_BY_LEVEL.keys())
    if rating <= levels[0]:
        return MAX_ACPL_BY_LEVEL[levels[0]]
    if rating >= levels[-1]:
        return MAX_ACPL_BY_LEVEL[levels[-1]]
    for i in range(len(levels) - 1):
        if levels[i] <= rating <= levels[i + 1]:
            lo, hi = levels[i], levels[i + 1]
            ratio = (rating - lo) / (hi - lo)
            return MAX_ACPL_BY_LEVEL[lo] + ratio * (MAX_ACPL_BY_LEVEL[hi] - MAX_ACPL_BY_LEVEL[lo])
    return MAX_ACPL_BY_LEVEL[1500]


def calculate_acpl(eval_diffs_cp: list[float]) -> float:
    """Calculate Average Centipawn Loss from a list of per-move eval differences."""
    if not eval_diffs_cp:
        return 0.0
    return sum(abs(d) for d in eval_diffs_cp) / len(eval_diffs_cp)


def calculate_dqm(eval_diffs_cp: list[float], rating: int = 1500) -> float:
    """Calculate DQM: normalized 0.0-1.0 score, level-relative."""
    acpl = calculate_acpl(eval_diffs_cp)
    max_acpl = _get_max_acpl(rating)
    dqm = max(0.0, min(1.0, 1.0 - (acpl / max_acpl)))
    return round(dqm, 3)
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_dqm_calculator.py -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add tools/dqm_calculator.py tests/test_dqm_calculator.py
git commit -m "feat: DQM calculator — level-relative decision quality metric"
```

---

### Task 9: Time analysis tool

**Files:**
- Create: `tools/time_analysis.py`
- Create: `tests/test_time_analysis.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_time_analysis.py
from tools.time_analysis import (
    calculate_time_per_move,
    detect_time_trouble,
    find_clock_inflection_point,
    classify_move_speed,
)

def test_time_per_move():
    clocks = [300, 290, 270, 240, 200, 150]
    times = calculate_time_per_move(clocks)
    assert times == [10, 20, 30, 40, 50]

def test_detect_time_trouble():
    clocks = [300, 250, 200, 100, 30, 10, 5]
    result = detect_time_trouble(clocks, threshold_seconds=60)
    assert result["in_time_trouble"] is True
    assert result["trouble_start_move"] == 4

def test_no_time_trouble():
    clocks = [300, 280, 260, 240, 220]
    result = detect_time_trouble(clocks, threshold_seconds=60)
    assert result["in_time_trouble"] is False

def test_find_clock_inflection():
    # Opponent spends more time progressively
    times_per_move = [5, 5, 10, 10, 15, 20, 60, 80, 90]
    inflection = find_clock_inflection_point(times_per_move)
    assert inflection is not None
    assert inflection >= 5

def test_classify_move_speed():
    assert classify_move_speed(3, is_complex=True) == "impulsive"
    assert classify_move_speed(900, is_complex=False) == "paralysis"
    assert classify_move_speed(60, is_complex=True) == "normal"
```

- [ ] **Step 2: Implement time_analysis.py**

```python
# tools/time_analysis.py
"""Analyze clock time patterns from chess games."""
from typing import Optional


def calculate_time_per_move(clock_readings: list[float]) -> list[float]:
    """Convert clock readings to time spent per move."""
    return [clock_readings[i] - clock_readings[i + 1] for i in range(len(clock_readings) - 1)]


def detect_time_trouble(clock_readings: list[float],
                        threshold_seconds: float = 60) -> dict:
    """Detect if and when a player enters time trouble."""
    for i, clock in enumerate(clock_readings):
        if clock <= threshold_seconds:
            return {
                "in_time_trouble": True,
                "trouble_start_move": i + 1,
                "remaining_at_trouble": clock,
            }
    return {"in_time_trouble": False, "trouble_start_move": None, "remaining_at_trouble": None}


def find_clock_inflection_point(time_per_move: list[float],
                                 window: int = 3) -> Optional[int]:
    """Find the move where time usage spikes (rolling average doubles)."""
    if len(time_per_move) < window * 2:
        return None
    for i in range(window, len(time_per_move) - window):
        avg_before = sum(time_per_move[i - window:i]) / window
        avg_after = sum(time_per_move[i:i + window]) / window
        if avg_before > 0 and avg_after / avg_before >= 2.0:
            return i + 1  # 1-indexed move number
    return None


def classify_move_speed(seconds_spent: float, is_complex: bool = False) -> str:
    """Classify a move's speed as impulsive, normal, or paralysis."""
    if seconds_spent < 10 and is_complex:
        return "impulsive"
    if seconds_spent > 600:  # 10+ minutes
        return "paralysis"
    return "normal"
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_time_analysis.py -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add tools/time_analysis.py tests/test_time_analysis.py
git commit -m "feat: time analysis — time trouble detection, inflection points, move speed"
```

---

### Task 10: Style classifier

**Files:**
- Create: `tools/style_classifier.py`
- Create: `tests/test_style_classifier.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_style_classifier.py
from tools.style_classifier import classify_style, classify_sub_profile

def test_activist():
    stats = {"avg_game_length": 28, "sacrifice_rate": 0.15, "initiative_moves_pct": 0.6}
    assert classify_style(stats) == "activist"

def test_theorist():
    stats = {"avg_game_length": 35, "sacrifice_rate": 0.02, "initiative_moves_pct": 0.3, "book_depth_avg": 18}
    assert classify_style(stats) == "theorist"

def test_defender():
    stats = {"avg_game_length": 45, "sacrifice_rate": 0.01, "initiative_moves_pct": 0.2}
    assert classify_style(stats) == "defender"

def test_precision_player():
    acpl_quiet = 15.0
    acpl_complex = 60.0
    assert classify_sub_profile(acpl_quiet, acpl_complex) == "precision_player"

def test_chaos_specialist():
    acpl_quiet = 55.0
    acpl_complex = 20.0
    assert classify_sub_profile(acpl_quiet, acpl_complex) == "chaos_specialist"

def test_balanced():
    acpl_quiet = 30.0
    acpl_complex = 35.0
    assert classify_sub_profile(acpl_quiet, acpl_complex) == "balanced"
```

- [ ] **Step 2: Implement style_classifier.py**

```python
# tools/style_classifier.py
"""Classify chess playing style into archetypes and sub-profiles."""


def classify_style(stats: dict) -> str:
    """Classify into activist/theorist/defender based on game stats."""
    sacrifice_rate = stats.get("sacrifice_rate", 0)
    initiative = stats.get("initiative_moves_pct", 0)
    avg_length = stats.get("avg_game_length", 35)
    book_depth = stats.get("book_depth_avg", 10)

    if sacrifice_rate > 0.08 and initiative > 0.45:
        return "activist"
    if book_depth > 14 and sacrifice_rate < 0.05:
        return "theorist"
    if avg_length > 40 and initiative < 0.3:
        return "defender"
    if initiative > 0.4:
        return "activist"
    return "theorist"


def classify_sub_profile(acpl_quiet: float, acpl_complex: float) -> str:
    """Classify as precision_player/chaos_specialist/balanced based on ACPL in different position types."""
    ratio = acpl_quiet / acpl_complex if acpl_complex > 0 else 1.0
    if ratio < 0.5:
        return "precision_player"
    if ratio > 1.5:
        return "chaos_specialist"
    return "balanced"
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_style_classifier.py -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add tools/style_classifier.py tests/test_style_classifier.py
git commit -m "feat: style classifier — archetype and sub-profile classification"
```

---

### Task 11: Error classifier

**Files:**
- Create: `tools/error_classifier.py`
- Create: `tests/test_error_classifier.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_error_classifier.py
from tools.error_classifier import classify_error

def test_impulsive_error():
    result = classify_error(eval_loss_cp=150, time_spent=5, is_complex=True)
    assert result["classification"] == "tactical_miss"
    assert result["behavioral"] == "impulsive"

def test_paralysis_error():
    result = classify_error(eval_loss_cp=80, time_spent=900, is_complex=False)
    assert result["classification"] == "conceptual_weakness"
    assert result["behavioral"] == "paralysis"

def test_time_pressure_error():
    result = classify_error(eval_loss_cp=200, time_spent=2, is_complex=True, clock_remaining=15)
    assert result["classification"] == "time_pressure"

def test_pattern_recognition():
    result = classify_error(eval_loss_cp=120, time_spent=30, is_complex=True,
                           maia_agrees=True, maia_level_match="lower")
    assert result["classification"] == "pattern_recognition_failure"

def test_minor_inaccuracy():
    result = classify_error(eval_loss_cp=25, time_spent=60, is_complex=False)
    assert result["severity"] == "minor"
```

- [ ] **Step 2: Implement error_classifier.py**

```python
# tools/error_classifier.py
"""Classify chess errors by cognitive origin and behavioral pattern."""
from typing import Optional


def classify_error(
    eval_loss_cp: float,
    time_spent: float,
    is_complex: bool = False,
    clock_remaining: Optional[float] = None,
    maia_agrees: bool = False,
    maia_level_match: Optional[str] = None,  # "lower", "same", "higher"
) -> dict:
    """Classify a chess error by type, severity, and behavioral pattern."""

    # Severity
    if eval_loss_cp < 50:
        severity = "minor"
    elif eval_loss_cp < 150:
        severity = "important"
    else:
        severity = "critical"

    # Behavioral pattern
    if time_spent < 10 and is_complex:
        behavioral = "impulsive"
    elif time_spent > 600:
        behavioral = "paralysis"
    else:
        behavioral = "normal"

    # Classification
    if clock_remaining is not None and clock_remaining < 30:
        classification = "time_pressure"
    elif maia_agrees and maia_level_match == "lower":
        classification = "pattern_recognition_failure"
    elif eval_loss_cp >= 100 and is_complex:
        classification = "tactical_miss"
    else:
        classification = "conceptual_weakness"

    return {
        "classification": classification,
        "severity": severity,
        "behavioral": behavioral,
        "eval_loss_cp": eval_loss_cp,
        "time_spent": time_spent,
    }
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_error_classifier.py -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add tools/error_classifier.py tests/test_error_classifier.py
git commit -m "feat: error classifier — cognitive origin and behavioral patterns"
```

---

### Task 12: Wellness tracker

**Files:**
- Create: `tools/wellness_tracker.py`
- Create: `tests/test_wellness_tracker.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_wellness_tracker.py
from tools.wellness_tracker import WellnessTracker

def test_from_manual():
    tracker = WellnessTracker()
    state = tracker.from_manual(sleep_hours=7, sleep_quality="good",
                                 energy_level=8, last_meal_hours_ago=1,
                                 hydration="adequate")
    assert state["sleep_hours"] == 7
    assert state["hrv"] is None

def test_from_wearable_not_implemented():
    tracker = WellnessTracker()
    try:
        tracker.from_wearable(device="oura")
        assert False, "Should raise NotImplementedError"
    except NotImplementedError:
        pass

def test_calculate_modifier_low_sleep():
    tracker = WellnessTracker()
    state = tracker.from_manual(sleep_hours=4, sleep_quality="poor",
                                 energy_level=3, last_meal_hours_ago=5,
                                 hydration="low")
    modifier = tracker.calculate_intensity_modifier(state)
    assert modifier <= 0.6

def test_calculate_modifier_good_state():
    tracker = WellnessTracker()
    state = tracker.from_manual(sleep_hours=8, sleep_quality="good",
                                 energy_level=9, last_meal_hours_ago=1,
                                 hydration="adequate")
    modifier = tracker.calculate_intensity_modifier(state)
    assert modifier >= 0.9

def test_generate_alerts():
    tracker = WellnessTracker()
    state = tracker.from_manual(sleep_hours=4, sleep_quality="poor",
                                 energy_level=3, last_meal_hours_ago=6,
                                 hydration="low")
    alerts = tracker.generate_alerts(state)
    assert len(alerts) >= 2
```

- [ ] **Step 2: Implement wellness_tracker.py**

```python
# tools/wellness_tracker.py
"""Track wellness state for biohacking recommendations."""
from typing import Optional


class WellnessTracker:
    """Collect and evaluate wellness data from manual input or wearables."""

    def from_manual(self, sleep_hours: float, sleep_quality: str,
                    energy_level: int, last_meal_hours_ago: float,
                    hydration: str, hrv: Optional[float] = None) -> dict:
        """Create wellness state from manual user input."""
        return {
            "sleep_hours": sleep_hours,
            "sleep_quality": sleep_quality,
            "hrv": hrv,
            "energy_level": energy_level,
            "last_meal_hours_ago": last_meal_hours_ago,
            "hydration": hydration,
        }

    def from_wearable(self, device: str, **kwargs) -> dict:
        """Create wellness state from wearable data. Not yet implemented."""
        raise NotImplementedError(
            f"Wearable integration for '{device}' is planned for a future phase. "
            "Supported devices will include: Oura Ring, WHOOP, Garmin. "
            "Use from_manual() for now."
        )

    def calculate_intensity_modifier(self, state: dict) -> float:
        """Calculate training intensity modifier (0.0-1.0) based on wellness state."""
        modifier = 1.0
        sleep = state.get("sleep_hours", 7)
        energy = state.get("energy_level", 7)
        quality = state.get("sleep_quality", "good")
        hydration = state.get("hydration", "adequate")

        if sleep < 5:
            modifier -= 0.4
        elif sleep < 6:
            modifier -= 0.25
        elif sleep < 7:
            modifier -= 0.1

        if quality == "poor":
            modifier -= 0.15
        elif quality == "fair":
            modifier -= 0.05

        if energy < 4:
            modifier -= 0.2
        elif energy < 6:
            modifier -= 0.1

        if hydration == "low":
            modifier -= 0.1

        return max(0.1, min(1.0, round(modifier, 2)))

    def generate_alerts(self, state: dict) -> list[str]:
        """Generate wellness alerts based on current state."""
        alerts = []
        if state.get("sleep_hours", 7) < 6:
            alerts.append("Low sleep detected — reduce new opening study, prioritize review")
        if state.get("energy_level", 7) < 5:
            alerts.append("Low energy — skip active calculation drills, focus on passive study")
        if state.get("hydration") == "low":
            alerts.append("Dehydration risk — drink water with electrolytes before studying")
        if state.get("last_meal_hours_ago", 0) > 4:
            alerts.append("Eat a balanced snack before starting — brain needs glucose")
        if state.get("sleep_quality") == "poor":
            alerts.append("Poor sleep quality — consider shorter study session with more breaks")
        return alerts
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_wellness_tracker.py -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add tools/wellness_tracker.py tests/test_wellness_tracker.py
git commit -m "feat: wellness tracker — manual input, intensity modifier, alerts"
```

---

## Chunk 3: Data Files, Templates & Agents

### Task 13: Static data files (supplements, nutrition protocols)

**Files:**
- Create: `data/supplements.json`
- Create: `data/nutrition_protocols.json`

- [ ] **Step 1: Create supplements.json**

Evidence-based supplement database with dosage, timing, and evidence level. Include: Creatine Monohydrate, L-Theanine + Caffeine, Omega-3 (DHA), Bacopa Monnieri, Magnesium, Vitamin B12, Vitamin D. Each entry: `name`, `dose`, `timing`, `purpose`, `evidence_level` (strong/moderate/emerging), `contraindications`, `notes`.

- [ ] **Step 2: Create nutrition_protocols.json**

Protocols by competition phase: `pre_tournament` (3 days before), `game_day` (breakfast, pre-round, during, post), `between_rounds`, `rest_day`. Each entry: `phase`, `timing`, `recommendation`, `rationale`.

- [ ] **Step 3: Commit**

```bash
git add data/supplements.json data/nutrition_protocols.json
git commit -m "feat: evidence-based supplements and nutrition protocol data"
```

---

### Task 14: Templates

**Files:**
- Create: `templates/intel_dossier.md`
- Create: `templates/game_review.md`
- Create: `templates/training_roadmap.md`
- Create: `templates/pre_game_protocol.md`

- [ ] **Step 1: Create intel_dossier.md template**

Template with placeholders: `{{username}}`, `{{platform}}`, `{{ratings}}`, `{{style_archetype}}`, `{{style_sub_profile}}`, `{{acpl_avg}}`, `{{opening_weaknesses}}`, `{{comfort_lines}}`, `{{clock_inflection_point}}`, `{{time_trouble_frequency}}`, `{{recent_form}}`. Sections: Player Profile, Rating History, Playing Style, Opening Weaknesses, Comfort Lines, Clock Management, Recommended Strategy.

- [ ] **Step 2: Create game_review.md template**

Placeholders: `{{game_id}}`, `{{result}}`, `{{acpl}}`, `{{dqm}}`, `{{critical_moments}}`, `{{opening_accuracy}}`, `{{middlegame_accuracy}}`, `{{endgame_accuracy}}`, `{{structure_played}}`, `{{recommended_study}}`. Sections: Game Summary, Critical Moments, Phase Accuracy, Training Recommendations.

- [ ] **Step 3: Create training_roadmap.md template**

Placeholders: `{{user_profile}}`, `{{phase_balance}}`, `{{active_weaknesses}}`, `{{strengths}}`, `{{next_session_plan}}`. Sections: Player Summary, Current Balance, Active Weaknesses, Strengths, Next Session Plan.

- [ ] **Step 4: Create pre_game_protocol.md template**

Placeholders: `{{opponent_dossier}}`, `{{opening_preparation}}`, `{{nutrition_protocol}}`, `{{supplementation}}`, `{{physical_protocol}}`, `{{mental_protocol}}`. Sections: Opponent Brief, Opening Plan, Pre-Game Nutrition, Supplements, Physical Routine, Mental Preparation.

- [ ] **Step 5: Commit**

```bash
git add templates/
git commit -m "feat: markdown templates for dossiers, reviews, roadmaps, protocols"
```

---

### Task 15: Agent definitions

**Files:**
- Create: `agents/intel.md`
- Create: `agents/gm.md`
- Create: `agents/mind.md`
- Create: `agents/biohack.md`

- [ ] **Step 1: Create agents/intel.md**

Agent prompt defining: role (Intelligence & Reconnaissance), available tools (lichess_client.py, chessdb_client.py, pgn_parser.py, time_analysis.py, style_classifier.py, opening_classifier.py, game_vault.py, ChessAgine MCP), output schema (player_report), key behaviors (Opening Explorer filtering, ACPL crossover analysis, clock inflection detection), instruction to respond in user's language.

- [ ] **Step 2: Create agents/gm.md**

Agent prompt defining: role (Grandmaster Analysis), tools (ChessAgine MCP, pgn_parser.py, error_classifier.py, dqm_calculator.py, opening_classifier.py, game_vault.py, tactics_generator.py), output schemas (game_analysis, training_insights), auto-analysis flow, DQM calculation, Maia comparison logic, instruction to respond in user's language.

- [ ] **Step 3: Create agents/mind.md**

Agent prompt defining: role (Mental Performance), tools (time_analysis.py, error_classifier.py, pgn_parser.py), output schema (mental_profile), tilt detection logic, decision pattern analysis, session recommendations, instruction to respond in user's language.

- [ ] **Step 4: Create agents/biohack.md**

Agent prompt defining: role (Biohacking & Performance), tools (wellness_tracker.py), data files (supplements.json, nutrition_protocols.json), output schema (biohack_protocol), intensity modifier logic, alert generation, instruction to respond in user's language.

- [ ] **Step 5: Commit**

```bash
git add agents/
git commit -m "feat: agent definitions — Intel, GM, Mind, Biohack"
```

---

### Task 16: Coordinator skill and hooks

**Files:**
- Create: `skills/coach/SKILL.md`
- Create: `hooks/hooks.json`
- Create: `tools/detect_pgn_save.py`

- [ ] **Step 1: Create skills/coach/SKILL.md**

Skill that acts as coordinator. Description for trigger: "Use when user asks about chess coaching, game analysis, opponent preparation, training plans, or chess-related wellness." Dispatches to agents based on intent detection (prep → Intel+GM+Biohack, review → GM+Mind, roadmap → GM+Mind+Biohack, intel → Intel, check-in → Biohack+GM, save → GM). Synthesizes agent outputs. Responds in user's language.

- [ ] **Step 2: Create hooks/hooks.json**

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/tools/validate_schema.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/tools/detect_pgn_save.py"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Create tools/detect_pgn_save.py**

```python
# tools/detect_pgn_save.py
"""Hook script: detect when a PGN file is written to the vault."""
import json
import sys
from pathlib import Path

from tools.pgn_parser import parse_pgn


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

    # Validate PGN
    if path.exists():
        content = path.read_text()
        game = parse_pgn(content)
        if game is None:
            print(f"WARNING: Invalid PGN written to vault: {file_path}", file=sys.stderr)
            sys.exit(2)  # Block — invalid PGN

    sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Commit**

```bash
git add skills/ hooks/ tools/detect_pgn_save.py
git commit -m "feat: coordinator skill, hooks, and PGN save detection"
```

---

## Chunk 4: Evals

### Task 17: Trigger evals for skill and agents

**Files:**
- Create: `skills/coach/eval-set.json`
- Create: `evals/intel/eval-set.json`
- Create: `evals/gm/eval-set.json`
- Create: `evals/mind/eval-set.json`
- Create: `evals/biohack/eval-set.json`

- [ ] **Step 1: Create skills/coach/eval-set.json**

10 positive cases (prep, review, roadmap, intel, save, check-in, import, add opponent, PGN paste, training question) + 10 negative cases (weather, code bug, email, cooking, general chat, math, history, travel, music, sports non-chess).

- [ ] **Step 2: Create evals/intel/eval-set.json**

8 positive (scout user, weakness analysis, import games, opening explorer, profile lookup, opponent prep, download games, style analysis) + 8 negative (analyze position, calculate DQM, nutrition advice, tilt detection, training plan, save game, Stockfish eval, endgame study).

- [ ] **Step 3: Create evals/gm/eval-set.json**

8 positive (analyze game, review PGN, find errors, create training plan, evaluate position, generate puzzles, opening repertoire, endgame analysis) + 8 negative (scout opponent, sleep advice, tilt detection, nutrition plan, download games, player profile, supplement recommendation, breathing exercise).

- [ ] **Step 4: Create evals/mind/eval-set.json**

8 positive (detect tilt, analyze time patterns, post-loss behavior, decision speed, emotional state, stress management, session readiness, resilience assessment) + 8 negative (analyze opening, Stockfish eval, nutrition advice, opponent scouting, save game, supplement recommendation, training plan, download games).

- [ ] **Step 5: Create evals/biohack/eval-set.json**

8 positive (nutrition plan, sleep assessment, supplement advice, pre-game protocol, energy level, hydration, recovery routine, training intensity) + 8 negative (analyze game, scout opponent, tilt detection, opening repertoire, download games, Stockfish eval, time pattern, error classification).

- [ ] **Step 6: Commit**

```bash
git add skills/coach/eval-set.json evals/
git commit -m "feat: trigger evals — 10+10 for coach, 8+8 per agent"
```

---

### Task 18: Quality evals

**Files:**
- Create: `skills/coach/evals/evals.json`
- Create: `evals/intel/evals.json`
- Create: `evals/gm/evals.json`
- Create: `evals/mind/evals.json`
- Create: `evals/biohack/evals.json`

- [ ] **Step 1: Create skills/coach/evals/evals.json**

5 quality eval cases as detailed in spec Section 9: pre-game prep, game review, biohack low sleep, tilt detection, save game. Each with 3-4 assertions (content_contains + llm_graded).

- [ ] **Step 2: Create per-agent quality evals**

For each agent, 3-5 eval cases testing their specific domain output quality with assertions matching their output schema.

- [ ] **Step 3: Commit**

```bash
git add skills/coach/evals/ evals/
git commit -m "feat: quality evals — assertion-based output verification"
```

---

## Chunk 5: Integration & Finalization

### Task 19: Tactics generator wrapper

**Files:**
- Create: `tools/tactics_generator.py`
- Create: `tests/test_tactics_generator.py`

- [ ] **Step 1: Write failing tests**

Test that `generate_puzzles_from_pgn()` extracts positions where eval swings by >150cp and returns puzzle dicts with `fen`, `solution`, `theme`.

- [ ] **Step 2: Implement tactics_generator.py**

Wrapper that uses python-chess + stockfish to find positions with large eval swings in a PGN. Returns puzzle positions. Falls back gracefully if Stockfish binary is not available.

- [ ] **Step 3: Run tests and commit**

```bash
git add tools/tactics_generator.py tests/test_tactics_generator.py
git commit -m "feat: tactics generator — puzzles from user blunders"
```

---

### Task 20: README and final integration

**Files:**
- Create: `README.md`
- Modify: `CLAUDE.md` (add setup instructions)

- [ ] **Step 1: Create README.md**

Sections: Overview, Features (4 agents), Quick Start (install plugin, prerequisites), Architecture diagram (text), Available Commands, Storage (Google Drive + local), Testing (pytest + evals), Contributing, License.

- [ ] **Step 2: Update CLAUDE.md with setup steps**

Add: prerequisite binaries (Stockfish 18, Node.js 24), `pip install -r requirements.txt`, ChessAgine MCP verification, vault setup.

- [ ] **Step 3: Run full test suite**

Run: `cd /Users/datoga/hack/chess-coach-ai && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 4: Final commit and push**

```bash
git add README.md CLAUDE.md
git commit -m "feat: README and finalized CLAUDE.md with setup instructions"
git push
```

---

## Task Summary

| Chunk | Tasks | Focus |
|-------|-------|-------|
| 1 | 1-7 | Scaffolding, schemas, PGN parser, opening classifier, Lichess client, ChessDB client, Game Vault |
| 2 | 8-12 | DQM calculator, time analysis, style classifier, error classifier, wellness tracker |
| 3 | 13-16 | Data files, templates, agent definitions, coordinator skill, hooks |
| 4 | 17-18 | Trigger evals + quality evals for all agents |
| 5 | 19-20 | Tactics generator, README, integration tests |

**Total: 20 tasks, ~100 steps**
