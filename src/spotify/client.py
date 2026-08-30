from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import spotipy


@dataclass
class Track:
    id: str
    name: str
    artist: str
    album: str
    duration_ms: int
    cover_url: str | None = None
    preview_url: str | None = None
    external_url: str | None = None

    @classmethod
    def from_spotify(cls, data: dict[str, Any]) -> Track:
        album = data.get("album", {})
        images = album.get("images", [])
        cover = images[0]["url"] if images else None
        artists = ", ".join(a["name"] for a in data.get("artists", []))
        return cls(id=data["id"], name=data["name"], artist=artists, album=album.get("name", ""), duration_ms=data.get("duration_ms", 0), cover_url=cover, preview_url=data.get("preview_url"), external_url=data.get("external_urls", {}).get("spotify"))


@dataclass
class PlaylistInfo:
    id: str
    name: str
    description: str | None = None
    cover_url: str | None = None
    track_count: int = 0
    tracks: list[Track] = field(default_factory=list)

    @classmethod
    def from_spotify(cls, data: dict[str, Any]) -> PlaylistInfo:
        images = data.get("images", [])
        return cls(id=data["id"], name=data["name"], description=data.get("description"), cover_url=images[0]["url"] if images else None, track_count=data.get("tracks", {}).get("total", 0))


@dataclass
class Artist:
    id: str
    name: str
    genres: list[str] = field(default_factory=list)
    image_url: str | None = None
    popularity: int = 0

    @classmethod
    def from_spotify(cls, data: dict[str, Any]) -> Artist:
        images = data.get("images", [])
        return cls(id=data["id"], name=data["name"], genres=data.get("genres", []), image_url=images[0]["url"] if images else None, popularity=data.get("popularity", 0))


class SpotifyClient:
    def __init__(self, access_token: str) -> None:
        self._sp = spotipy.Spotify(auth=access_token)

    def search(self, query: str, search_type: str = "track", limit: int = 20) -> dict[str, list[Any]]:
        results = self._sp.search(q=query, type=search_type, limit=limit)
        parsed: dict[str, list[Any]] = {}
        if "tracks" in results:
            parsed["tracks"] = [Track.from_spotify(t) for t in results["tracks"]["items"]]
        if "artists" in results:
            parsed["artists"] = [Artist.from_spotify(a) for a in results["artists"]["items"]]
        if "playlists" in results:
            parsed["playlists"] = [PlaylistInfo.from_spotify(p) for p in results["playlists"]["items"]]
        return parsed

    def get_track(self, track_id: str) -> Track:
        return Track.from_spotify(self._sp.track(track_id))

    def get_user_playlists(self, limit: int = 50) -> list[PlaylistInfo]:
        return [PlaylistInfo.from_spotify(p) for p in self._sp.current_user_playlists(limit=limit)["items"]]

    def get_playlist_tracks(self, playlist_id: str) -> list[Track]:
        return [Track.from_spotify(item["track"]) for item in self._sp.playlist_tracks(playlist_id)["items"] if item["track"]]

    def create_playlist(self, name: str, description: str = "") -> PlaylistInfo:
        user = self._sp.current_user()
        return PlaylistInfo.from_spotify(self._sp.user_playlist_create(user["id"], name=name, public=False, description=description))

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str]) -> None:
        self._sp.playlist_add_items(playlist_id, track_ids)

    def get_recently_played(self, limit: int = 50) -> list[Track]:
        return [Track.from_spotify(item["track"]) for item in self._sp.current_user_recently_played(limit=limit)["items"]]

    def get_top_tracks(self, limit: int = 50, time_range: str = "medium_term") -> list[Track]:
        return [Track.from_spotify(t) for t in self._sp.current_user_top_tracks(limit=limit, time_range=time_range)["items"]]

    def get_recommendations(self, seed_tracks: list[str] | None = None, seed_artists: list[str] | None = None, seed_genres: list[str] | None = None, limit: int = 20) -> list[Track]:
        kwargs: dict[str, Any] = {"limit": limit}
        if seed_tracks: kwargs["seed_tracks"] = seed_tracks[:5]
        if seed_artists: kwargs["seed_artists"] = seed_artists[:5]
        if seed_genres: kwargs["seed_genres"] = seed_genres[:5]
        return [Track.from_spotify(t) for t in self._sp.recommendations(**kwargs)["tracks"]]

    def get_available_genres(self) -> list[str]:
        return self._sp.available_genre_seeds().get("genres", [])
