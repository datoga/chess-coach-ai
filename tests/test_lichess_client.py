import pytest
from unittest.mock import MagicMock, patch
from tools.lichess_client import LichessClient

@pytest.fixture
def client():
    return LichessClient()

def test_get_profile(client):
    with patch.object(client, '_client') as mock:
        mock.users.get_public_data.return_value = {
            "id": "testuser", "username": "TestUser",
            "perfs": {"blitz": {"rating": 1500}, "rapid": {"rating": 1600}}
        }
        profile = client.get_profile("testuser")
        assert profile["username"] == "TestUser"
        assert "ratings" in profile
        assert profile["ratings"]["blitz"] == 1500

def test_get_recent_games(client):
    with patch.object(client, '_client') as mock:
        mock.games.export_by_player.return_value = iter([
            {"id": "game1", "moves": "e4 e5", "players": {}}
        ])
        games = client.get_recent_games("testuser", max_games=1)
        assert len(games) == 1

def test_get_opening_explorer(client):
    with patch.object(client, '_request_explorer') as mock:
        mock.return_value = {
            "moves": [{"uci": "e2e4", "san": "e4", "white": 100, "draws": 50, "black": 50}]
        }
        result = client.get_opening_explorer("testuser", color="white")
        assert len(result["moves"]) > 0

def test_profile_missing_perfs(client):
    with patch.object(client, '_client') as mock:
        mock.users.get_public_data.return_value = {
            "id": "newuser", "username": "NewUser", "perfs": {}
        }
        profile = client.get_profile("newuser")
        assert profile["ratings"]["blitz"] == 0
