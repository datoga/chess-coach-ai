"""Generate tactical puzzles from PGN games by detecting large eval swings."""
import shutil
from typing import Optional

import chess
import chess.pgn

from tools.pgn_parser import parse_pgn


def _is_stockfish_available() -> bool:
    """Check if Stockfish binary is available on the system."""
    return shutil.which("stockfish") is not None


def _analyze_position(board: chess.Board) -> Optional[int]:
    """Analyze a position with Stockfish. Returns eval in centipawns from white's perspective."""
    try:
        from stockfish import Stockfish
        sf = Stockfish(path=shutil.which("stockfish"), depth=15)
        sf.set_fen_position(board.fen())
        evaluation = sf.get_evaluation()
        if evaluation["type"] == "cp":
            return evaluation["value"]
        elif evaluation["type"] == "mate":
            return 10000 if evaluation["value"] > 0 else -10000
        return None
    except Exception:
        return None


def generate_puzzles_from_pgn(pgn_text: str, threshold_cp: int = 150) -> list[dict]:
    """Find positions with large eval swings in a PGN game and return puzzle dicts.

    Args:
        pgn_text: PGN string of the game
        threshold_cp: Minimum centipawn swing to flag as a puzzle position

    Returns:
        List of puzzle dicts with fen, move_number, blunder_move, solution, eval_swing_cp, theme
    """
    if not _is_stockfish_available():
        return []

    game = parse_pgn(pgn_text)
    if game is None:
        return []

    puzzles = []
    board = game.board()
    prev_eval: Optional[int] = None
    move_num = 0

    for move in game.mainline_moves():
        move_num += 1
        san = board.san(move)
        fen_before = board.fen()
        board.push(move)
        current_eval = _analyze_position(board)

        if prev_eval is not None and current_eval is not None:
            # Eval swing: measure how much the position changed (absolute)
            # A large swing indicates a blunder or missed tactic
            swing = abs(current_eval - prev_eval)

            if swing >= threshold_cp:
                # This was a blunder — the position before was the puzzle
                puzzles.append({
                    "fen": fen_before,
                    "move_number": (move_num + 1) // 2,
                    "blunder_move": san,
                    "solution": "Find the best move in this position",
                    "eval_swing_cp": abs(swing),
                    "theme": _classify_theme(swing),
                })

        prev_eval = current_eval

    return puzzles


def _classify_theme(swing_cp: int) -> str:
    """Classify the tactical theme based on eval swing magnitude."""
    if abs(swing_cp) >= 500:
        return "critical_blunder"
    elif abs(swing_cp) >= 300:
        return "major_tactical_miss"
    else:
        return "tactical_opportunity"
