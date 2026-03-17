"""Parse PGN games into structured data with clock times and game phases."""
import io
import re
import chess.pgn


def parse_pgn(pgn_text: str) -> chess.pgn.Game | None:
    """Parse a PGN string into a python-chess Game object."""
    try:
        game = chess.pgn.read_game(io.StringIO(pgn_text))
        if game is None:
            return None
        # Reject input that produced only default placeholder headers and no moves
        default_values = {"?", "*", "????.??.??"}
        has_real_headers = any(
            v not in default_values for v in game.headers.values()
        )
        has_moves = bool(game.variations)
        if not has_real_headers and not has_moves:
            return None
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
