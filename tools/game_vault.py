"""Game vault: local PGN storage with Google Drive interface."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from tools.pgn_parser import parse_pgn
from tools.opening_classifier import classify_opening


class GameVault:
    def __init__(self, local_path: Optional[Path] = None, gdrive_enabled: bool = False):
        self.local_path = local_path or Path(__file__).parent.parent / "vault"
        self.gdrive_enabled = gdrive_enabled
        self._ensure_dirs()

    def save_game(self, pgn_text: str, category: str = "my_game",
                  opponent: Optional[str] = None) -> dict:
        game = parse_pgn(pgn_text)
        game_id = hashlib.sha256(pgn_text.encode()).hexdigest()[:16]
        now = datetime.now(timezone.utc).isoformat()

        opening = {"eco": "A00", "name": "Unknown"}
        if game:
            moves_list = list(game.mainline_moves())
            if moves_list:
                board = game.board()
                san_moves = []
                for m in moves_list[:15]:
                    san_moves.append(board.san(m))
                    board.push(m)
                pgn_str = ""
                for i, san in enumerate(san_moves):
                    if i % 2 == 0:
                        pgn_str += f"{i // 2 + 1}. {san} "
                    else:
                        pgn_str += f"{san} "
                opening = classify_opening(pgn_str.strip())

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

        (subdir / filename).write_text(pgn_text)

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

        self._update_index(entry)

        if self.gdrive_enabled:
            try:
                self._sync_to_gdrive(entry, pgn_text)
                entry["sync_status"] = "synced"
            except Exception:
                entry["sync_status"] = "local_only"

        return entry

    def list_games(self, category: Optional[str] = None) -> list[dict]:
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
        (self.local_path / "index.json").write_text(json.dumps(index, indent=2))

    def _sync_to_gdrive(self, entry: dict, pgn_text: str):
        raise NotImplementedError(
            "Google Drive sync requires OAuth2 credentials. "
            "Set up credentials.json and run the auth flow.")
