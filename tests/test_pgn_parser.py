import chess.pgn
from tools.pgn_parser import parse_pgn, extract_moves_with_clocks, get_game_phases

SAMPLE_PGN = """[Event "Rated Blitz game"]
[White "player1"]
[Black "player2"]
[Result "1-0"]
[WhiteElo "1500"]
[BlackElo "1450"]
[ECO "B01"]
[TimeControl "300+0"]

1. e4 {[%clk 0:04:58]} d5 {[%clk 0:04:55]} 2. exd5 {[%clk 0:04:50]} Qxd5 {[%clk 0:04:48]} 3. Nc3 {[%clk 0:04:45]} Qa5 {[%clk 0:04:40]} 1-0"""

def test_parse_pgn_returns_game():
    game = parse_pgn(SAMPLE_PGN)
    assert game is not None
    assert game.headers["White"] == "player1"
    assert game.headers["Result"] == "1-0"

def test_parse_pgn_invalid():
    result = parse_pgn("not a pgn")
    assert result is None

def test_extract_moves_with_clocks():
    game = parse_pgn(SAMPLE_PGN)
    moves = extract_moves_with_clocks(game)
    assert len(moves) == 6
    assert moves[0]["san"] == "e4"
    assert moves[0]["clock_seconds"] is not None

def test_get_game_phases():
    game = parse_pgn(SAMPLE_PGN)
    phases = get_game_phases(game)
    assert "opening" in phases
    assert "middlegame" in phases
    assert "endgame" in phases
    assert len(phases["opening"]) == 6  # all 6 moves are in opening (moves 1-3)
