"""Safe Stockfish evaluation wrapper with hard timeout. Use this instead of running stockfish via bash."""
import shutil
from typing import Optional


def is_available() -> bool:
    """Check if Stockfish binary is available on the system."""
    return shutil.which("stockfish") is not None


def evaluate_position(fen: str, depth: int = 18, timeout_sec: int = 15) -> Optional[dict]:
    """Evaluate a position with Stockfish. Returns dict with eval and best move, or None on failure.

    Args:
        fen: FEN string of the position
        depth: Search depth (default 18, max 25)
        timeout_sec: Hard timeout in seconds (default 15)

    Returns:
        {"eval_cp": int, "eval_type": "cp"|"mate", "best_move": str, "pv": str} or None
    """
    if not is_available():
        return None

    try:
        from stockfish import Stockfish
        sf = Stockfish(
            path=shutil.which("stockfish"),
            depth=min(depth, 25),
            parameters={"Threads": 1, "Hash": 64}
        )
        sf.set_fen_position(fen)

        evaluation = sf.get_evaluation()
        best_move = sf.get_best_move_time(timeout_sec * 1000)
        top_moves = sf.get_top_moves(1)

        pv = ""
        if top_moves:
            pv = top_moves[0].get("Move", "")

        return {
            "eval_type": evaluation["type"],
            "eval_cp": evaluation["value"],
            "best_move": best_move,
            "pv": pv,
            "depth": depth,
        }
    except Exception as e:
        return None


def evaluate_game(pgn_text: str, depth: int = 15, timeout_per_move: int = 10) -> list[dict]:
    """Evaluate all positions in a PGN game. Returns list of per-move evaluations.

    Args:
        pgn_text: PGN string
        depth: Search depth per move
        timeout_per_move: Timeout per position in seconds

    Returns:
        List of {"move_number": int, "color": str, "san": str, "eval_cp": int, "best_move": str}
    """
    if not is_available():
        return []

    from tools.pgn_parser import parse_pgn

    game = parse_pgn(pgn_text)
    if game is None:
        return []

    try:
        from stockfish import Stockfish
        sf = Stockfish(
            path=shutil.which("stockfish"),
            depth=min(depth, 25),
            parameters={"Threads": 1, "Hash": 64}
        )
    except Exception:
        return []

    results = []
    board = game.board()
    move_num = 0

    for move in game.mainline_moves():
        move_num += 1
        san = board.san(move)

        try:
            sf.set_fen_position(board.fen())
            evaluation = sf.get_evaluation()
            best = sf.get_best_move_time(timeout_per_move * 1000)

            results.append({
                "move_number": (move_num + 1) // 2,
                "color": "white" if move_num % 2 == 1 else "black",
                "san": san,
                "fen_before": board.fen(),
                "eval_type": evaluation["type"],
                "eval_cp": evaluation["value"],
                "best_move": best,
                "played_is_best": move.uci() == best if best else False,
            })
        except Exception:
            results.append({
                "move_number": (move_num + 1) // 2,
                "color": "white" if move_num % 2 == 1 else "black",
                "san": san,
                "fen_before": board.fen(),
                "eval_type": "error",
                "eval_cp": 0,
                "best_move": None,
                "played_is_best": False,
            })

        board.push(move)

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: stockfish_eval.py <FEN>")
        print("       stockfish_eval.py --game <PGN_FILE>")
        sys.exit(1)

    if sys.argv[1] == "--game" and len(sys.argv) > 2:
        import json
        pgn = open(sys.argv[2]).read()
        results = evaluate_game(pgn)
        print(json.dumps(results, indent=2))
    else:
        fen = sys.argv[1]
        result = evaluate_position(fen)
        if result:
            print(f"Eval: {result['eval_cp']}cp ({result['eval_type']})")
            print(f"Best: {result['best_move']}")
        else:
            print("Stockfish not available or evaluation failed")
