#!/usr/bin/env python3
"""Verify chess-coach-ai prerequisites and report status."""
import json
import shutil
import subprocess
import sys
from pathlib import Path


def check_binary(name: str, version_flag: str = "--version") -> dict:
    """Check if a binary is available and get its version."""
    path = shutil.which(name)
    if not path:
        return {"installed": False, "path": None, "version": None}
    try:
        result = subprocess.run(
            [path, version_flag],
            capture_output=True, text=True, timeout=5
        )
        version = (result.stdout + result.stderr).strip().split("\n")[0]
        return {"installed": True, "path": path, "version": version}
    except Exception:
        return {"installed": True, "path": path, "version": "unknown"}


def check_stockfish() -> dict:
    """Check Stockfish installation."""
    path = shutil.which("stockfish")
    if not path:
        return {"installed": False, "path": None, "version": None}
    try:
        result = subprocess.run(
            ["stockfish"],
            input="uci\nquit\n",
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            if line.startswith("id name"):
                version = line.replace("id name ", "")
                return {"installed": True, "path": path, "version": version}
        return {"installed": True, "path": path, "version": "unknown"}
    except Exception:
        return {"installed": True, "path": path, "version": "unknown"}


def check_python_deps() -> list[dict]:
    """Check Python dependencies from requirements.txt."""
    results = []
    req_file = Path(__file__).parent.parent / "requirements.txt"
    if not req_file.exists():
        return [{"name": "requirements.txt", "installed": False, "note": "File not found"}]

    for line in req_file.read_text().strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pkg_name = line.split(">=")[0].split("==")[0].split("<")[0].strip()
        try:
            __import__(pkg_name.replace("-", "_"))
            results.append({"name": pkg_name, "installed": True})
        except ImportError:
            results.append({"name": pkg_name, "installed": False})
    return results


def check_chessagine_mcp() -> dict:
    """Check if ChessAgine MCP can be started."""
    node = shutil.which("node") or shutil.which("nodejs")
    npx = shutil.which("npx")
    if not node:
        return {"available": False, "reason": "Node.js not installed"}
    if not npx:
        return {"available": False, "reason": "npx not found"}
    return {"available": True, "reason": "npx available, ChessAgine MCP can be started"}


def check_lc0() -> dict:
    """Check lc0 (Leela Chess Zero) for Maia models."""
    return check_binary("lc0")


def check_openings_data() -> dict:
    """Check if lichess-org/chess-openings data is present."""
    openings_dir = Path(__file__).parent.parent / "data" / "openings"
    tsv_files = list(openings_dir.glob("*.tsv")) if openings_dir.exists() else []
    return {
        "available": len(tsv_files) >= 5,
        "files": len(tsv_files),
        "path": str(openings_dir),
    }


def check_vault() -> dict:
    """Check vault directory status."""
    vault = Path(__file__).parent.parent / "vault"
    return {
        "exists": vault.exists(),
        "has_games": (vault / "my-games").exists() and any((vault / "my-games").iterdir()) if (vault / "my-games").exists() else False,
        "has_index": (vault / "index.json").exists(),
        "path": str(vault),
    }


def run_all_checks() -> dict:
    """Run all prerequisite checks and return full report."""
    return {
        "stockfish": check_stockfish(),
        "node": check_binary("node"),
        "python": check_binary("python3"),
        "chessagine_mcp": check_chessagine_mcp(),
        "lc0": check_lc0(),
        "python_deps": check_python_deps(),
        "openings_data": check_openings_data(),
        "vault": check_vault(),
    }


def print_report(report: dict):
    """Print a human-readable setup report."""
    print("=" * 60)
    print("  Chess Coach AI — Setup Status")
    print("=" * 60)

    # Stockfish
    sf = report["stockfish"]
    status = "✅" if sf["installed"] else "❌"
    print(f"\n{status} Stockfish: {sf.get('version', 'not installed')}")
    if not sf["installed"]:
        print("   Install: brew install stockfish")

    # Node.js
    node = report["node"]
    status = "✅" if node["installed"] else "❌"
    print(f"{status} Node.js: {node.get('version', 'not installed')}")
    if not node["installed"]:
        print("   Install: brew install node")

    # ChessAgine MCP
    mcp = report["chessagine_mcp"]
    status = "✅" if mcp["available"] else "❌"
    print(f"{status} ChessAgine MCP: {mcp['reason']}")
    if not mcp["available"]:
        print("   Requires Node.js. Then: npx -y chessagine-mcp")

    # lc0 (optional)
    lc0 = report["lc0"]
    status = "✅" if lc0["installed"] else "⚠️ "
    label = lc0.get("version", "not installed") if lc0["installed"] else "not installed (optional, for Maia models)"
    print(f"{status} lc0: {label}")
    if not lc0["installed"]:
        print("   Optional install: brew install lc0")

    # Python deps
    print(f"\n📦 Python Dependencies:")
    deps = report["python_deps"]
    all_ok = True
    for dep in deps:
        status = "✅" if dep["installed"] else "❌"
        print(f"   {status} {dep['name']}")
        if not dep["installed"]:
            all_ok = False
    if not all_ok:
        print("   Fix: pip install -r requirements.txt")

    # Openings data
    od = report["openings_data"]
    status = "✅" if od["available"] else "❌"
    print(f"\n{status} Opening database: {od['files']} TSV files")
    if not od["available"]:
        print("   Missing lichess-org/chess-openings data in data/openings/")

    # Vault
    vault = report["vault"]
    status = "✅" if vault["exists"] else "❌"
    print(f"{status} Game Vault: {'ready' if vault['exists'] else 'missing'}")
    if vault["has_games"]:
        print(f"   Has games stored")
    if vault["has_index"]:
        print(f"   Index file present")

    # Summary
    print("\n" + "=" * 60)
    critical = [
        report["stockfish"]["installed"],
        report["node"]["installed"],
        report["chessagine_mcp"]["available"],
        all_ok,
        report["openings_data"]["available"],
    ]
    if all(critical):
        print("✅ All critical prerequisites met. Ready to use!")
    else:
        missing = sum(1 for c in critical if not c)
        print(f"❌ {missing} critical issue(s) found. Fix them before using the plugin.")
    print("=" * 60)


if __name__ == "__main__":
    report = run_all_checks()
    if "--json" in sys.argv:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
