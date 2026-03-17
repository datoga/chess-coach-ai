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
