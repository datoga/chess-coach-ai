"""Render chess boards as Unicode art for terminal display. Use sparingly — only for critical positions."""
import chess


def render_board(fen: str, perspective: str = "white", highlight_squares: list[str] = None,
                 label: str = None) -> str:
    """Render a chess board as Unicode art for terminal display.

    Args:
        fen: FEN string of the position
        perspective: "white" or "black" (board orientation)
        highlight_squares: List of square names to mark (e.g., ["e4", "d5"])
        label: Optional label shown above the board (e.g., "Move 23 — Critical moment")

    Returns:
        Unicode string representation of the board
    """
    try:
        board = chess.Board(fen)
    except ValueError:
        return f"Invalid FEN: {fen}"

    highlight_set = set()
    if highlight_squares:
        for sq_name in highlight_squares:
            try:
                highlight_set.add(chess.parse_square(sq_name))
            except ValueError:
                pass

    piece_map = {
        "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙",
        "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
    }

    ranks = range(8) if perspective == "black" else range(7, -1, -1)
    files = range(7, -1, -1) if perspective == "black" else range(8)

    lines = []

    if label:
        lines.append(f"  ╔═══ {label} ═══╗")
        lines.append("")

    lines.append("  ┌───┬───┬───┬───┬───┬───┬───┬───┐")

    for i, rank in enumerate(ranks):
        row = f"{rank + 1} │"
        for file in files:
            sq = chess.square(file, rank)
            piece = board.piece_at(sq)
            if piece:
                symbol = piece_map.get(piece.symbol(), "?")
            else:
                symbol = " "

            if sq in highlight_set:
                row += f"*{symbol}*│"
            else:
                row += f" {symbol} │"

        lines.append(row)
        if i < 7:
            lines.append("  ├───┼───┼───┼───┼───┼───┼───┼───┤")

    lines.append("  └───┴───┴───┴───┴───┴───┴───┴───┘")

    if perspective == "black":
        lines.append("    h   g   f   e   d   c   b   a")
    else:
        lines.append("    a   b   c   d   e   f   g   h")

    turn = "White" if board.turn else "Black"
    lines.append(f"  {turn} to move")

    return "\n".join(lines)


def render_comparison(fen: str, played_move: str, best_move: str,
                      played_eval: str = None, best_eval: str = None,
                      label: str = None) -> str:
    """Render a position with played vs best move comparison.

    Args:
        fen: FEN before the move
        played_move: SAN of the move played (e.g., "Nf3")
        best_move: SAN of the best move (e.g., "d5")
        played_eval: Eval after played move (e.g., "-1.2")
        best_eval: Eval after best move (e.g., "+0.5")
        label: Position label

    Returns:
        Formatted comparison string with board
    """
    board_str = render_board(fen, label=label)

    comparison = [
        board_str,
        "",
        f"  ❌ Played: {played_move}" + (f"  ({played_eval})" if played_eval else ""),
        f"  ✅ Best:   {best_move}" + (f"  ({best_eval})" if best_eval else ""),
    ]

    return "\n".join(comparison)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        fen = chess.STARTING_FEN
    else:
        fen = sys.argv[1]

    highlights = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    label = sys.argv[3] if len(sys.argv) > 3 else None

    print(render_board(fen, highlight_squares=highlights, label=label))
