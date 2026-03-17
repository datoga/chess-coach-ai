"""Endgame tablebase lookup via Lichess Syzygy API + optional local tables.

Supports up to 7 pieces. Uses Lichess API (free, no auth) with fallback
to local Syzygy tables if installed.

Results: exact game-theoretic evaluation (win/draw/loss) with DTZ
(distance to zeroing) and optimal move.
"""
import requests
from typing import Optional
from pathlib import Path

import chess
import chess.syzygy

LICHESS_TB_URL = "https://tablebase.lichess.ovh/standard"
LOCAL_PATHS = [
    Path.home() / ".local" / "share" / "syzygy",
    Path("/usr/local/share/syzygy"),
    Path("/opt/homebrew/share/syzygy"),
]


def _find_local_tables() -> Optional[Path]:
    """Find local Syzygy tablebase directory."""
    for path in LOCAL_PATHS:
        if path.exists() and any(path.glob("*.rtbw")):
            return path
    custom = Path(__file__).parent.parent / "data" / "syzygy"
    if custom.exists() and any(custom.glob("*.rtbw")):
        return custom
    return None


def probe_online(fen: str, timeout: int = 10) -> Optional[dict]:
    """Probe position via Lichess Syzygy API.

    Args:
        fen: FEN string (must be <= 7 pieces)
        timeout: Request timeout in seconds

    Returns:
        {
            "category": "win"|"draw"|"loss"|"cursed-win"|"blessed-loss",
            "dtz": int or None (distance to zeroing),
            "best_move": str (UCI),
            "checkmate": bool,
            "stalemate": bool,
            "moves": [{"uci": str, "category": str, "dtz": int}...]
        }
        or None on failure
    """
    try:
        resp = requests.get(LICHESS_TB_URL, params={"fen": fen}, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        best_move = None
        if data.get("moves"):
            # First move in the list is the best
            best_move = data["moves"][0].get("uci")

        return {
            "category": data.get("category", "unknown"),
            "dtz": data.get("dtz"),
            "best_move": best_move,
            "checkmate": data.get("checkmate", False),
            "stalemate": data.get("stalemate", False),
            "insufficient_material": data.get("insufficient_material", False),
            "moves": [
                {"uci": m["uci"], "category": m.get("category", "unknown"), "dtz": m.get("dtz")}
                for m in data.get("moves", [])[:10]
            ],
        }
    except Exception:
        return None


def probe_local(fen: str) -> Optional[dict]:
    """Probe position via local Syzygy tables.

    Returns:
        {"category": "win"|"draw"|"loss", "dtz": int} or None
    """
    tb_path = _find_local_tables()
    if not tb_path:
        return None

    try:
        board = chess.Board(fen)
        with chess.syzygy.open_tablebase(str(tb_path)) as tb:
            dtz = tb.probe_dtz(board)
            wdl = tb.probe_wdl(board)

            if wdl > 0:
                category = "win"
            elif wdl < 0:
                category = "loss"
            else:
                category = "draw"

            return {"category": category, "dtz": dtz}
    except Exception:
        return None


def probe(fen: str) -> Optional[dict]:
    """Probe position using best available source (online preferred, local fallback).

    Args:
        fen: FEN string (must be <= 7 pieces)

    Returns:
        Tablebase result dict or None
    """
    # Count pieces
    board = chess.Board(fen)
    piece_count = len(board.piece_map())
    if piece_count > 7:
        return None  # Tablebases only cover up to 7 pieces

    # Try online first (richer data: moves, DTZ per move)
    result = probe_online(fen)
    if result:
        result["source"] = "lichess_api"
        return result

    # Fallback to local
    result = probe_local(fen)
    if result:
        result["source"] = "local_syzygy"
        return result

    return None


def is_available() -> dict:
    """Check tablebase availability."""
    local_path = _find_local_tables()
    online = False
    try:
        resp = requests.get(LICHESS_TB_URL, params={"fen": "4k3/8/8/8/8/8/8/4K2R w K - 0 1"}, timeout=5)
        online = resp.status_code == 200
    except Exception:
        pass

    return {
        "online": online,
        "online_url": LICHESS_TB_URL,
        "local": local_path is not None,
        "local_path": str(local_path) if local_path else None,
    }


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: tablebase.py <FEN>")
        print("       tablebase.py --check")
        sys.exit(1)

    if sys.argv[1] == "--check":
        status = is_available()
        print(f"Online (Lichess API): {'✅' if status['online'] else '❌'}")
        print(f"Local Syzygy tables:  {'✅ ' + status['local_path'] if status['local'] else '❌ not found'}")
        sys.exit(0)

    fen = sys.argv[1]
    result = probe(fen)
    if result:
        print(f"Result: {result['category']} (DTZ: {result.get('dtz', '?')})")
        if result.get("best_move"):
            print(f"Best move: {result['best_move']}")
        if result.get("moves"):
            print("Top moves:")
            for m in result["moves"][:5]:
                print(f"  {m['uci']}: {m['category']} (DTZ: {m.get('dtz', '?')})")
        print(f"Source: {result.get('source', 'unknown')}")
    else:
        board = chess.Board(fen)
        pieces = len(board.piece_map())
        if pieces > 7:
            print(f"Position has {pieces} pieces — tablebases only cover up to 7")
        else:
            print("Tablebase lookup failed")
