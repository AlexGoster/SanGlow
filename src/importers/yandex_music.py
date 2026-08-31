from __future__ import annotations

import re
from urllib.parse import quote

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class Track:
    id: str
    title: str
    artist: str
    album: str
    duration_ms: int
    cover_url: str | None = None
    source: str = "yandex"

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.title, "artist": self.artist, "album": self.album, "duration_ms": self.duration_ms, "cover_url": self.cover_url, "source": self.source}


class YandexMusicImporter:
    BASE_URL = "https://api.music.yandex.net"

    def __init__(self, auth_token: str | None = None) -> None:
        headers = {"User-Agent": "Yandex-Music-API", "Accept": "application/json"}
        if auth_token:
            headers["Authorization"] = f"OAuth {auth_token}"
        self._client = httpx.Client(headers=headers, follow_redirects=True, timeout=30)

    def search(self, query: str, limit: int = 20) -> list[Track]:
        try:
            response = self._client.get(f"{self.BASE_URL}/search", params={"text": query, "type": "track", "page": 0})
            response.raise_for_status()
            return self._parse_tracks(response.json(), limit)
        except Exception:
            return []

    def import_from_url(self, url: str) -> list[Track]:
        match = re.search(r"playlist/([a-zA-Z0-9_-]+):([a-zA-Z0-9_-]+)", url)
        if match:
            try:
                user_id = quote(match.group(1), safe="")
                playlist_id = quote(match.group(2), safe="")
                response = self._client.get(f"{self.BASE_URL}/users/{user_id}/playlists/{playlist_id}")
                response.raise_for_status()
                return [t for item in response.json().get("result", {}).get("tracks", []) if (t := self._parse_track(item.get("track", item))) is not None]
            except Exception:
                return []
        return []

    def _parse_tracks(self, data: dict[str, Any], limit: int) -> list[Track]:
        return [t for item in data.get("result", {}).get("tracks", {}).get("results", [])[:limit] if (t := self._parse_track(item)) is not None]

    def _parse_track(self, data: dict[str, Any]) -> Track | None:
        try:
            artists = data.get("artists", [])
            albums = data.get("albums", [])
            cover = data.get("coverUri", "")
            return Track(id=str(data.get("id", "")), title=data.get("title", ""), artist=artists[0].get("name", "") if artists else "", album=albums[0].get("title", "") if albums else "", duration_ms=data.get("durationMs", 0), cover_url=f"https://{cover.replace('%%', '400x400')}" if cover else None)
        except (IndexError, KeyError):
            return None

    def close(self) -> None:
        self._client.close()
