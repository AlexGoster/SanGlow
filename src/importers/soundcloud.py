from __future__ import annotations

import os
import re
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
    audio_url: str | None = None
    source: str = "soundcloud"

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.title, "artist": self.artist, "album": self.album, "duration_ms": self.duration_ms, "cover_url": self.cover_url, "preview_url": self.audio_url, "source": self.source}


class SoundCloudImporter:
    BASE_URL = "https://api-v2.soundcloud.com"

    def __init__(self) -> None:
        self._client_id = os.environ.get("SOUNDCLOUD_CLIENT_ID", "")
        self._client = httpx.Client(headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True)

    def search(self, query: str, limit: int = 20) -> list[Track]:
        if not self._client_id:
            return []
        try:
            response = self._client.get(f"{self.BASE_URL}/tracks", params={"q": query, "client_id": self._client_id, "limit": limit})
            response.raise_for_status()
            return [t for item in response.json()[:limit] if (t := self._parse_track(item)) is not None]
        except Exception:
            return []

    def import_from_url(self, url: str) -> list[Track]:
        if not self._client_id:
            return []
        if not re.match(r"^https?://(www\.)?soundcloud\.com/", url):
            return []
        try:
            response = self._client.get("https://api.soundcloud.com/resolve", params={"url": url, "client_id": self._client_id})
            response.raise_for_status()
            data = response.json()
            if "tracks" in data:
                return [t for item in data["tracks"] if (t := self._parse_track(item)) is not None]
            track = self._parse_track(data)
            return [track] if track else []
        except Exception:
            return []

    def _parse_track(self, data: dict[str, Any]) -> Track | None:
        try:
            artwork = data.get("artwork_url", "")
            if artwork:
                artwork = artwork.replace("-large", "-t300x300")
            stream = data.get("stream_url", "")
            if stream and "?" not in stream:
                stream = f"{stream}?client_id={self._client_id}"
            return Track(id=str(data.get("id", "")), title=data.get("title", ""), artist=data.get("user", {}).get("username", ""), album="", duration_ms=data.get("duration", 0), cover_url=artwork, audio_url=stream)
        except (IndexError, KeyError):
            return None

    def close(self) -> None:
        self._client.close()
