from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re

try:
    from zvuk_music import Client, Quality
    ZVUK_AVAILABLE = True
except ImportError:
    ZVUK_AVAILABLE = False


@dataclass
class Track:
    id: str
    title: str
    artist: str
    album: str
    duration_ms: int
    cover_url: str | None = None
    source: str = "zvuk"

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.title, "artist": self.artist, "album": self.album, "duration_ms": self.duration_ms, "cover_url": self.cover_url, "source": self.source}


class ZvukMusicImporter:
    def __init__(self, token: str | None = None) -> None:
        if not ZVUK_AVAILABLE:
            raise ImportError("pip install zvuk-music")
        self._client = Client(token=token or Client.get_anonymous_token())

    def search(self, query: str, limit: int = 20) -> list[Track]:
        try:
            return [self._parse_track(t) for t in self._client.quick_search(query, limit=limit).tracks[:limit]]
        except Exception:
            return []

    def get_playlist(self, playlist_id: str) -> list[Track]:
        try:
            return [self._parse_track(t) for t in self._client.get_playlist(int(playlist_id)).tracks]
        except Exception:
            return []

    def get_liked_tracks(self, limit: int = 50) -> list[Track]:
        try:
            return [self._parse_track(t) for t in self._client.get_liked_tracks()[:limit]]
        except Exception:
            return []

    def get_stream_url(self, track_id: str, quality: str = "mid") -> str | None:
        try:
            q = {"mid": Quality.MID, "high": Quality.HIGH, "flac": Quality.FLAC}.get(quality, Quality.MID)
            return self._client.get_stream_url(int(track_id), quality=q)
        except Exception:
            return None

    def import_from_url(self, url: str) -> list[Track]:
        playlist_match = re.search(r"playlist/(\d+)", url)
        if playlist_match:
            return self.get_playlist(playlist_match.group(1))
        track_match = re.search(r"track/(\d+)", url)
        if track_match:
            try:
                return [self._parse_track(self._client.get_track(int(track_match.group(1))))]
            except Exception:
                return []
        return []

    def _parse_track(self, track: Any) -> Track:
        try:
            artists = getattr(track, "artists", [])
            releases = getattr(track, "releases", [])
            cover = None
            if releases and hasattr(releases[0], "cover"):
                c = getattr(releases[0], "cover", None)
                if c:
                    cover = getattr(c, "url", None)
            return Track(id=str(getattr(track, "id", "")), title=getattr(track, "title", ""), artist=artists[0].title if artists else "", album=releases[0].title if releases else "", duration_ms=getattr(track, "duration", 0) * 1000, cover_url=cover)
        except (IndexError, AttributeError):
            return Track(id="", title="Unknown", artist="Unknown", album="", duration_ms=0)
