#!/usr/bin/env python3
"""Verify chess-coach-ai prerequisites and report status."""
import json
import shutil
import subprocess
import sys
from pathlib import Path


def check_stockfish() -> dict:
    """Check Stockfish installation (native + WASM fallback)."""
    # Native
    path = shutil.which("stockfish")
    native = False
    version = None
    if path:
        try:
            result = subprocess.run(
                ["stockfish"],
                input="uci\nquit\n",
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split("\n"):
                if line.startswith("id name"):
                    version = line.replace("id name ", "")
            native = True
        except Exception:
            native = True
            version = "unknown"

    # WASM fallback
    wasm_runner = Path(__file__).parent.parent / "vendor" / "stockfish-wasm" / "run.js"
    wasm = wasm_runner.exists() and shutil.which("node") is not None

    return {
        "installed": native or wasm,
        "native": native,
        "wasm": wasm,
        "path": path,
        "version": version or ("WASM (bundled)" if wasm else None),
    }


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


def check_tablebase() -> dict:
    """Check endgame tablebase availability."""
    import importlib.util
    tb_path = Path(__file__).parent / "tablebase.py"
    spec = importlib.util.spec_from_file_location("tablebase", tb_path)
    tb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tb)
    return tb.is_available()


def run_all_checks() -> dict:
    """Run all prerequisite checks and return full report."""
    return {
        "stockfish": check_stockfish(),
        "python_deps": check_python_deps(),
        "openings_data": check_openings_data(),
        "tablebase": check_tablebase(),
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
    if sf.get("native"):
        print(f"   Native binary: {sf['path']}")
    if sf.get("wasm"):
        print(f"   WASM fallback: bundled (vendor/stockfish-wasm/)")
    if not sf["installed"]:
        print("   Install: brew install stockfish (or WASM fallback will be used if Node.js is available)")

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

    # Tablebase
    tb = report["tablebase"]
    online_status = "✅" if tb["online"] else "❌"
    local_status = "✅" if tb["local"] else "⚠️ "
    print(f"\n{online_status} Tablebase API (Lichess): {'available' if tb['online'] else 'unreachable'}")
    print(f"{local_status} Local Syzygy tables: {tb.get('local_path', 'not installed (optional)')}")
    if not tb["local"]:
        print("   Optional: download 3-4-5 piece tables to ~/.local/share/syzygy/")

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
