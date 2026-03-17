"""Safe Stockfish evaluation wrapper with analysis depth profiles.

Fallback chain:
  1. Native Stockfish binary (fastest, best)
  2. Stockfish WASM via Node.js (bundled in vendor/, no install needed)
  3. chessdb.cn cloud eval (no local engine at all)

Analysis modes:
  - quick:  ~30s total for a full game. Depth 10, 0.5s per move.
  - normal: ~1-2 min total. Depth 15, 1.5s per move.
  - deep:   ~2-3 min total. Depth 20, 3s per move.
"""
import shutil
import subprocess
import time
import re
from pathlib import Path
from typing import Optional

PROFILES = {
    "quick":  {"depth": 10, "time_ms": 500,  "budget_sec": 30},
    "normal": {"depth": 15, "time_ms": 1500, "budget_sec": 120},
    "deep":   {"depth": 20, "time_ms": 3000, "budget_sec": 180},
}

WASM_DIR = Path(__file__).parent.parent / "vendor" / "stockfish-wasm"
WASM_RUNNER = WASM_DIR / "run.js"


def _has_native() -> bool:
    """Check if native Stockfish binary is available."""
    return shutil.which("stockfish") is not None


def _has_wasm() -> bool:
    """Check if Stockfish WASM is available."""
    return WASM_RUNNER.exists() and shutil.which("node") is not None


def is_available() -> bool:
    """Check if any Stockfish engine is available (native or WASM)."""
    return _has_native() or _has_wasm()


def get_engine_type() -> str:
    """Return which engine will be used."""
    if _has_native():
        return "native"
    if _has_wasm():
        return "wasm"
    return "none"


def _create_engine(profile: str = "normal"):
    """Create a native Stockfish instance."""
    from stockfish import Stockfish
    p = PROFILES.get(profile, PROFILES["normal"])
    threads = 1 if profile == "quick" else 2
    hash_mb = 32 if profile == "quick" else 128
    return Stockfish(
        path=shutil.which("stockfish"),
        depth=p["depth"],
        parameters={"Threads": threads, "Hash": hash_mb}
    )


def _eval_wasm(fen: str, depth: int = 15, time_ms: int = 1500) -> Optional[dict]:
    """Evaluate a position using Stockfish WASM via Node.js subprocess."""
    if not _has_wasm():
        return None

    commands = f"uci\nisready\nposition fen {fen}\ngo depth {depth}\nquit\n"

    try:
        result = subprocess.run(
            ["node", str(WASM_RUNNER)],
            input=commands,
            capture_output=True, text=True,
            timeout=max(time_ms / 1000 * 2, 10),  # 2x time budget or 10s min
        )

        output = result.stdout
        best_move = None
        eval_cp = 0
        eval_type = "cp"

        for line in output.split("\n"):
            # Parse "bestmove e2e4"
            if line.startswith("bestmove"):
                parts = line.split()
                if len(parts) >= 2:
                    best_move = parts[1]

            # Parse deepest "info depth ... score cp/mate ..."
            if "score" in line and "info depth" in line:
                score_match = re.search(r"score (cp|mate) (-?\d+)", line)
                if score_match:
                    eval_type = score_match.group(1)
                    val = int(score_match.group(2))
                    if eval_type == "mate":
                        eval_cp = 10000 if val > 0 else -10000
                    else:
                        eval_cp = val

        if best_move:
            return {
                "eval_type": eval_type,
                "eval_cp": eval_cp,
                "best_move": best_move,
                "top_moves": [],
                "profile": "wasm",
            }
        return None
    except Exception:
        return None


def evaluate_position(fen: str, profile: str = "normal") -> Optional[dict]:
    """Evaluate a single position with Stockfish (native → WASM fallback).

    Args:
        fen: FEN string of the position
        profile: "quick" (0.5s), "normal" (1.5s), or "deep" (3s)

    Returns:
        {"eval_cp": int, "eval_type": "cp"|"mate", "best_move": str, "top_moves": list, "engine": str} or None
    """
    if not is_available():
        return None

    p = PROFILES.get(profile, PROFILES["normal"])

    # Try native first
    if _has_native():
        try:
            sf = _create_engine(profile)
            sf.set_fen_position(fen)

            evaluation = sf.get_evaluation()
            best_move = sf.get_best_move_time(p["time_ms"])
            top_moves = sf.get_top_moves(3)

            return {
                "eval_type": evaluation["type"],
                "eval_cp": evaluation["value"],
                "best_move": best_move,
                "top_moves": [{"move": m["Move"], "cp": m.get("Centipawn", 0)} for m in top_moves],
                "profile": profile,
                "engine": "native",
            }
        except Exception:
            pass  # Fall through to WASM

    # Fallback to WASM
    if _has_wasm():
        result = _eval_wasm(fen, depth=p["depth"], time_ms=p["time_ms"])
        if result:
            result["engine"] = "wasm"
            return result

    return None


def evaluate_game(pgn_text: str, profile: str = "normal") -> dict:
    """Evaluate all positions in a PGN game with time budget control.

    Args:
        pgn_text: PGN string
        profile: "quick" (~30s), "normal" (~1-2min), or "deep" (~2-3min)

    Returns:
        {
            "moves": [per-move eval list],
            "summary": {"acpl_white": float, "acpl_black": float, "total_time": float},
            "profile": str,
            "total_moves": int,
            "analyzed_moves": int
        }
    """
    if not is_available():
        return {"moves": [], "summary": {}, "profile": profile, "total_moves": 0, "analyzed_moves": 0}

    from tools.pgn_parser import parse_pgn

    game = parse_pgn(pgn_text)
    if game is None:
        return {"moves": [], "summary": {}, "profile": profile, "total_moves": 0, "analyzed_moves": 0}

    p = PROFILES.get(profile, PROFILES["normal"])
    total_moves = sum(1 for _ in game.mainline_moves())

    # Calculate adaptive time per move based on budget
    if total_moves > 0:
        time_per_move_ms = min(p["time_ms"], int((p["budget_sec"] * 1000) / total_moves))
        # Minimum 200ms per move even in quick mode
        time_per_move_ms = max(200, time_per_move_ms)
    else:
        return {"moves": [], "summary": {}, "profile": profile, "total_moves": 0, "analyzed_moves": 0}

    try:
        sf = _create_engine(profile)
    except Exception:
        return {"moves": [], "summary": {}, "profile": profile, "total_moves": total_moves, "analyzed_moves": 0}

    results = []
    board = game.board()
    move_num = 0
    start_time = time.time()
    prev_eval = None
    white_losses = []
    black_losses = []

    for move in game.mainline_moves():
        move_num += 1
        elapsed = time.time() - start_time

        # Hard budget check — stop analyzing if over budget
        if elapsed > p["budget_sec"]:
            # Mark remaining moves as not analyzed
            san = board.san(move)
            results.append({
                "move_number": (move_num + 1) // 2,
                "color": "white" if move_num % 2 == 1 else "black",
                "san": san,
                "analyzed": False,
            })
            board.push(move)
            continue

        san = board.san(move)

        try:
            sf.set_fen_position(board.fen())
            evaluation = sf.get_evaluation()
            best = sf.get_best_move_time(time_per_move_ms)

            eval_cp = evaluation["value"] if evaluation["type"] == "cp" else (10000 if evaluation["value"] > 0 else -10000)

            # Calculate centipawn loss vs previous position
            cp_loss = 0
            if prev_eval is not None:
                if move_num % 2 == 1:  # White moved
                    cp_loss = max(0, prev_eval - eval_cp)
                    white_losses.append(cp_loss)
                else:  # Black moved
                    cp_loss = max(0, eval_cp - prev_eval)
                    black_losses.append(cp_loss)

            results.append({
                "move_number": (move_num + 1) // 2,
                "color": "white" if move_num % 2 == 1 else "black",
                "san": san,
                "fen_before": board.fen(),
                "eval_type": evaluation["type"],
                "eval_cp": eval_cp,
                "best_move": best,
                "played_is_best": move.uci() == best if best else False,
                "cp_loss": cp_loss,
                "analyzed": True,
            })

            prev_eval = eval_cp

        except Exception:
            results.append({
                "move_number": (move_num + 1) // 2,
                "color": "white" if move_num % 2 == 1 else "black",
                "san": san,
                "analyzed": False,
            })

        board.push(move)

    total_time = time.time() - start_time
    analyzed = sum(1 for r in results if r.get("analyzed", False))

    summary = {
        "acpl_white": round(sum(white_losses) / len(white_losses), 1) if white_losses else 0,
        "acpl_black": round(sum(black_losses) / len(black_losses), 1) if black_losses else 0,
        "total_time_sec": round(total_time, 1),
        "time_per_move_ms": time_per_move_ms,
    }

    return {
        "moves": results,
        "summary": summary,
        "profile": profile,
        "total_moves": total_moves,
        "analyzed_moves": analyzed,
    }


if __name__ == "__main__":
    import sys
    import json

    usage = """Usage:
  stockfish_eval.py <FEN> [quick|normal|deep]
  stockfish_eval.py --game <PGN_FILE> [quick|normal|deep]

Profiles:
  quick   ~30s total, depth 10  — rapid overview
  normal  ~1-2min total, depth 15  — standard review (default)
  deep    ~2-3min total, depth 20  — full analysis"""

    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)

    if sys.argv[1] == "--game" and len(sys.argv) > 2:
        pgn = open(sys.argv[2]).read()
        profile = sys.argv[3] if len(sys.argv) > 3 else "normal"
        result = evaluate_game(pgn, profile=profile)
        print(f"Profile: {result['profile']} | Moves: {result['analyzed_moves']}/{result['total_moves']} | Time: {result['summary'].get('total_time_sec', 0)}s")
        print(f"ACPL White: {result['summary'].get('acpl_white', 0)} | ACPL Black: {result['summary'].get('acpl_black', 0)}")
        print(json.dumps(result, indent=2))
    else:
        fen = sys.argv[1]
        profile = sys.argv[2] if len(sys.argv) > 2 else "normal"
        result = evaluate_position(fen, profile=profile)
        if result:
            print(f"Eval: {result['eval_cp']}cp ({result['eval_type']}) [{profile}]")
            print(f"Best: {result['best_move']}")
            if result.get("top_moves"):
                for m in result["top_moves"]:
                    print(f"  {m['move']}: {m['cp']}cp")
        else:
            print("Stockfish not available or evaluation failed")
