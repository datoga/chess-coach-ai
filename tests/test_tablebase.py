from unittest.mock import patch, MagicMock
from tools.tablebase import probe_online, probe_local, probe, is_available

KR_VS_K = "4k3/8/8/8/8/8/8/4K2R w K - 0 1"

def test_probe_online_success():
    with patch("tools.tablebase.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "category": "win", "dtz": 12, "checkmate": False,
                "stalemate": False, "insufficient_material": False,
                "moves": [{"uci": "h1h7", "category": "win", "dtz": -11}]
            }
        )
        mock_get.return_value.raise_for_status = MagicMock()
        result = probe_online(KR_VS_K)
        assert result["category"] == "win"
        assert result["best_move"] == "h1h7"

def test_probe_online_failure():
    with patch("tools.tablebase.requests.get", side_effect=Exception("timeout")):
        result = probe_online(KR_VS_K)
        assert result is None

def test_probe_too_many_pieces():
    starting = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    result = probe(starting)
    assert result is None

def test_probe_fallback():
    with patch("tools.tablebase.probe_online", return_value=None):
        with patch("tools.tablebase.probe_local", return_value={"category": "draw", "dtz": 0}):
            result = probe(KR_VS_K)
            assert result["category"] == "draw"
            assert result["source"] == "local_syzygy"

def test_is_available():
    status = is_available()
    assert "online" in status
    assert "local" in status
