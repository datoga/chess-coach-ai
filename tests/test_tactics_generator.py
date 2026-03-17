import pytest
from unittest.mock import patch, MagicMock
from tools.tactics_generator import generate_puzzles_from_pgn, _is_stockfish_available

SAMPLE_PGN = """[Event "Test"]
[White "p1"]
[Black "p2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 1-0"""

def test_generate_puzzles_no_stockfish():
    """Without Stockfish, should return empty list gracefully."""
    with patch("tools.tactics_generator._is_stockfish_available", return_value=False):
        puzzles = generate_puzzles_from_pgn(SAMPLE_PGN)
        assert puzzles == []

def test_generate_puzzles_with_mock_engine():
    """With a mocked engine, should detect eval swings."""
    with patch("tools.tactics_generator._is_stockfish_available", return_value=True):
        with patch("tools.tactics_generator._analyze_position") as mock_analyze:
            # Simulate an eval swing: position was +0.3, then after a move it's -2.0
            evals = [30, 30, 30, 30, 30, -200, 30, 30, 30, 30]
            mock_analyze.side_effect = evals
            puzzles = generate_puzzles_from_pgn(SAMPLE_PGN, threshold_cp=150)
            assert len(puzzles) >= 1
            assert "fen" in puzzles[0]
            assert "solution" in puzzles[0]
            assert "eval_swing_cp" in puzzles[0]

def test_generate_puzzles_no_blunders():
    """When all evals are stable, no puzzles generated."""
    with patch("tools.tactics_generator._is_stockfish_available", return_value=True):
        with patch("tools.tactics_generator._analyze_position") as mock_analyze:
            mock_analyze.return_value = 30  # all positions eval +0.3
            puzzles = generate_puzzles_from_pgn(SAMPLE_PGN, threshold_cp=150)
            assert puzzles == []

def test_puzzle_structure():
    """Verify puzzle dict has expected keys."""
    with patch("tools.tactics_generator._is_stockfish_available", return_value=True):
        with patch("tools.tactics_generator._analyze_position") as mock_analyze:
            evals = [30, 30, 30, 30, 30, -300, 30, 30, 30, 30]
            mock_analyze.side_effect = evals
            puzzles = generate_puzzles_from_pgn(SAMPLE_PGN, threshold_cp=150)
            if puzzles:
                p = puzzles[0]
                assert "fen" in p
                assert "move_number" in p
                assert "blunder_move" in p
                assert "solution" in p
                assert "eval_swing_cp" in p
                assert "theme" in p
