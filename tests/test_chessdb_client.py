from unittest.mock import patch, MagicMock
from tools.chessdb_client import ChessDBClient

def test_query_position():
    client = ChessDBClient()
    with patch("tools.chessdb_client.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"status": "ok", "moves": [
                {"uci": "e2e4", "score": 30, "rank": 0}
            ]}
        )
        mock_get.return_value.raise_for_status = MagicMock()
        result = client.query_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        assert result["status"] == "ok"
        assert len(result["moves"]) > 0

def test_get_best_move():
    client = ChessDBClient()
    with patch("tools.chessdb_client.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            text="bestmove:e2e4"
        )
        mock_get.return_value.raise_for_status = MagicMock()
        move = client.get_best_move("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        assert move == "e2e4"

def test_fallback_on_timeout():
    client = ChessDBClient()
    with patch("tools.chessdb_client.requests.get", side_effect=Exception("timeout")):
        result = client.query_position("some_fen")
        assert result is None

def test_best_move_fallback():
    client = ChessDBClient()
    with patch("tools.chessdb_client.requests.get", side_effect=Exception("timeout")):
        result = client.get_best_move("some_fen")
        assert result is None
