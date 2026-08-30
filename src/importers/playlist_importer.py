from __future__ import annotations

import json
import csv
import os
from pathlib import Path
from typing import Any

from src.spotify.client import SpotifyClient, PlaylistInfo


class PlaylistImporter:
    def __init__(self, spotify_client: SpotifyClient) -> None:
        self._spotify = spotify_client

    def import_from_spotify(self, playlist_id: str) -> PlaylistInfo:
        tracks = self._spotify.get_playlist_tracks(playlist_id)
        playlist = PlaylistInfo.from_spotify(self._spotify._sp.playlist(playlist_id))
        playlist.tracks = tracks
        return playlist

    def import_from_url(self, url: str) -> PlaylistInfo | None:
        if "open.spotify.com/playlist/" in url:
            parts = url.split("playlist/")
            if len(parts) > 1:
                return self.import_from_spotify(parts[1].split("?")[0])
        return None

    def _validate_output_path(self, output_path: str) -> Path:
        resolved = Path(output_path).resolve()
        try:
            resolved.relative_to(Path.cwd().resolve())
        except ValueError:
            raise ValueError(f"Output path must be within the working directory: {output_path}")
        return resolved

    def export_to_json(self, playlist: PlaylistInfo, output_path: str) -> None:
        safe_path = self._validate_output_path(output_path)
        data = {"name": playlist.name, "description": playlist.description, "tracks": [{"id": t.id, "name": t.name, "artist": t.artist} for t in playlist.tracks]}
        safe_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def export_to_csv(self, playlist: PlaylistInfo, output_path: str) -> None:
        safe_path = self._validate_output_path(output_path)
        with open(safe_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Artist", "Album", "Duration (ms)", "Spotify ID"])
            for track in playlist.tracks:
                writer.writerow([track.name, track.artist, track.album, track.duration_ms, track.id])

    def sync_to_spotify(self, playlist: PlaylistInfo) -> PlaylistInfo:
        new_playlist = self._spotify.create_playlist(playlist.name, playlist.description or "Imported by SanGlow")
        if playlist.tracks:
            self._spotify.add_tracks_to_playlist(new_playlist.id, [t.id for t in playlist.tracks])
        return new_playlist
