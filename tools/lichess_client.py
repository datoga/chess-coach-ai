"""Lichess API client using berserk library."""
import json
import berserk
import requests
from typing import Optional


class LichessClient:
    """Wrapper around berserk for Lichess API access."""

    def __init__(self, token: Optional[str] = None):
        session = berserk.TokenSession(token) if token else None
        self._client = berserk.Client(session)

    def get_profile(self, username: str) -> dict:
        """Get player profile with ratings."""
        data = self._client.users.get_public_data(username)
        perfs = data.get("perfs", {})
        return {
            "username": data.get("username", username),
            "platform": "lichess",
            "ratings": {
                tc: perfs.get(tc, {}).get("rating", 0)
                for tc in ["bullet", "blitz", "rapid", "classical"]
            },
            "title": data.get("title"),
            "online": data.get("online", False),
            "last_seen": data.get("seenAt"),
        }

    def get_recent_games(self, username: str, max_games: int = 50,
                         time_control: Optional[str] = None) -> list[dict]:
        """Export recent games for a player."""
        kwargs = {"max": max_games, "clocks": True, "evals": True, "opening": True}
        if time_control:
            kwargs["perf_type"] = time_control
        games = list(self._client.games.export_by_player(username, **kwargs))
        return games

    def get_opening_explorer(self, username: str, color: str = "white",
                              speeds: Optional[list[str]] = None) -> dict:
        """Query the Lichess Opening Explorer for a specific player."""
        params = {"player": username, "color": color}
        if speeds:
            params["speeds"] = ",".join(speeds)
        return self._request_explorer(params)

    def _request_explorer(self, params: dict) -> dict:
        """Raw request to Lichess Opening Explorer API.

        The player endpoint can return NDJSON (multiple JSON lines).
        We parse only the first line which contains the root position data.
        """
        url = "https://explorer.lichess.ovh/player"
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        # Handle NDJSON: parse first line only (root position)
        text = resp.text.strip()
        first_line = text.split("\n")[0]
        return json.loads(first_line)
