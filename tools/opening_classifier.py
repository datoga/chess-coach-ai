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
