from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re

import httpx


@dataclass
class Track:
    id: str
    title: str
    artist: str
    album: str
    duration_ms: int
    source: str = "telegram"

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.title, "artist": self.artist, "album": self.album, "duration_ms": self.duration_ms, "source": self.source}


class TelegramMusicImporter:
    def __init__(self) -> None:
        self._client = httpx.Client(headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True, timeout=30)

    def search_public_channels(self, query: str, limit: int = 20) -> list[Track]:
        tracks = []
        for channel in ["musicalbums", "hot_musictracks", "new_music_releases"]:
            try:
                response = self._client.get(f"https://t.me/s/{channel}")
                response.raise_for_status()
                for match in re.finditer(r"<audio[^>]*>.*?</audio>", response.text, re.DOTALL):
                    block = match.group()
                    title = re.search(r'data-title="([^"]*)"', block)
                    performer = re.search(r'data-performer="([^"]*)"', block)
                    duration = re.search(r'data-duration="(\d+)"', block)
                    t = title.group(1) if title else "Unknown"
                    a = performer.group(1) if performer else "Unknown"
                    d = int(duration.group(1)) * 1000 if duration else 0
                    if query.lower() in t.lower() or query.lower() in a.lower():
                        tracks.append(Track(id=f"tg_{hash(t + a)}", title=t, artist=a, album="", duration_ms=d))
                        if len(tracks) >= limit:
                            return tracks
            except Exception:
                continue
        return tracks

    def import_from_url(self, url: str) -> list[Track]:
        match = re.match(r"https?://t\.me/([a-zA-Z0-9_]{1,64})", url)
        if not match:
            return []
        try:
            response = self._client.get(f"https://t.me/s/{match.group(1)}")
            response.raise_for_status()
            tracks = []
            for m in re.finditer(r"<audio[^>]*>.*?</audio>", response.text, re.DOTALL):
                block = m.group()
                title = re.search(r'data-title="([^"]*)"', block)
                performer = re.search(r'data-performer="([^"]*)"', block)
                duration = re.search(r'data-duration="(\d+)"', block)
                t = title.group(1) if title else "Unknown"
                a = performer.group(1) if performer else "Unknown"
                d = int(duration.group(1)) * 1000 if duration else 0
                tracks.append(Track(id=f"tg_{hash(t + a)}", title=t, artist=a, album="", duration_ms=d))
            return tracks
        except Exception:
            return []

    def close(self) -> None:
        self._client.close()
