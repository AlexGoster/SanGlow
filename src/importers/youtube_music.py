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
    cover_url: str | None = None
    audio_url: str | None = None
    source: str = "youtube"

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.title, "artist": self.artist, "album": self.album, "duration_ms": self.duration_ms, "cover_url": self.cover_url, "preview_url": self.audio_url, "source": self.source}


class YouTubeMusicImporter:
    BASE_URL = "https://music.youtube.com"

    def __init__(self) -> None:
        self._client = httpx.Client(headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}, follow_redirects=True)

    def search(self, query: str, limit: int = 20) -> list[Track]:
        try:
            response = self._client.post(f"{self.BASE_URL}/youtubei/v1/search", json={"query": query, "params": "EgWKAQIIAWoKEAMQBBAJEAoQBQ%3D%3D"})
            response.raise_for_status()
            return self._parse_tracks(response.json(), limit)
        except Exception:
            return []

    def import_from_url(self, url: str) -> list[Track]:
        match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
        if not match:
            return []
        try:
            response = self._client.post(f"{self.BASE_URL}/youtubei/v1/browse", json={"browseId": "VL" + match.group(1)})
            response.raise_for_status()
            return self._parse_playlist_tracks(response.json())
        except Exception:
            return []

    def _parse_tracks(self, data: dict[str, Any], limit: int) -> list[Track]:
        tracks = []
        for section in data.get("contents", {}).get("twoColumnSearchResultsRenderer", {}).get("primaryContents", {}).get("sectionListRenderer", {}).get("contents", []):
            for item in section.get("itemSectionRenderer", {}).get("contents", [])[:limit]:
                renderer = item.get("musicResponsiveListItemRenderer", {})
                if renderer:
                    track = self._parse_track_renderer(renderer)
                    if track:
                        tracks.append(track)
                        if len(tracks) >= limit:
                            return tracks
        return tracks

    def _parse_track_renderer(self, renderer: dict[str, Any]) -> Track | None:
        try:
            cols = renderer.get("flexColumns", [])
            title = cols[0].get("musicResponsiveListItemFlexColumnRenderer", {}).get("text", {}).get("runs", [{}])[0].get("text", "") if cols else ""
            artist = cols[1].get("musicResponsiveListItemFlexColumnRenderer", {}).get("text", {}).get("runs", [{}])[0].get("text", "") if len(cols) > 1 else ""
            vid = renderer.get("playlistItemData", {}).get("videoId", "")
            thumbs = renderer.get("thumbnail", {}).get("musicThumbnailRenderer", {}).get("thumbnail", {}).get("thumbnails", [])
            return Track(id=vid, title=title, artist=artist, album="", duration_ms=0, cover_url=thumbs[-1].get("url") if thumbs else None, source="youtube_music")
        except (IndexError, KeyError):
            return None

    def _parse_playlist_tracks(self, data: dict[str, Any]) -> list[Track]:
        tracks = []
        contents = data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [{}])[0].get("tabRenderer", {}).get("content", {}).get("sectionListRenderer", {}).get("contents", [{}])[0].get("musicPlaylistShelfRenderer", {}).get("contents", [])
        for item in contents:
            renderer = item.get("musicResponsiveListItemRenderer", {})
            if renderer:
                track = self._parse_track_renderer(renderer)
                if track:
                    tracks.append(track)
        return tracks

    def close(self) -> None:
        self._client.close()
