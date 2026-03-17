import json
import tempfile
from pathlib import Path
from tools.game_vault import GameVault

SAMPLE_PGN = '[Event "Test"]\n[White "p1"]\n[Black "p2"]\n[Result "1-0"]\n[TimeControl "300+0"]\n\n1. e4 e5 2. Nf3 Nc6 1-0'

def test_save_my_game(tmp_path):
    vault = GameVault(local_path=tmp_path)
    entry = vault.save_game(SAMPLE_PGN, category="my_game")
    assert entry["category"] == "my_game"
    pgn_path = tmp_path / entry["pgn_file"]
    assert pgn_path.exists()

def test_save_opponent_game(tmp_path):
    vault = GameVault(local_path=tmp_path)
    entry = vault.save_game(SAMPLE_PGN, category="opponent_prep", opponent="magnus")
    assert entry["category"] == "opponent_prep"
    assert "magnus" in entry["pgn_file"]

def test_index_updated(tmp_path):
    vault = GameVault(local_path=tmp_path)
    vault.save_game(SAMPLE_PGN, category="my_game")
    index = json.loads((tmp_path / "index.json").read_text())
    assert len(index) == 1

def test_list_games(tmp_path):
    vault = GameVault(local_path=tmp_path)
    vault.save_game(SAMPLE_PGN, category="my_game")
    vault.save_game(SAMPLE_PGN, category="opponent_prep", opponent="bob")
    games = vault.list_games()
    assert len(games) == 2

def test_list_games_filtered(tmp_path):
    vault = GameVault(local_path=tmp_path)
    vault.save_game(SAMPLE_PGN, category="my_game")
    vault.save_game(SAMPLE_PGN, category="opponent_prep", opponent="bob")
    my_games = vault.list_games(category="my_game")
    assert len(my_games) == 1

def test_google_drive_fallback(tmp_path):
    vault = GameVault(local_path=tmp_path, gdrive_enabled=True)
    entry = vault.save_game(SAMPLE_PGN, category="my_game")
    assert entry["sync_status"] == "local_only"
