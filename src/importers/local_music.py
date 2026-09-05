from __future__ import annotations

import os
import json
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Any

AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac", ".wma", ".opus"}


@dataclass
class LocalTrack:
    id: str
    name: str
    artist: str
    album: str
    duration_ms: int
    local_path: str
    source: str = "local"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "artist": self.artist,
            "album": self.album,
            "duration_ms": self.duration_ms,
            "local_path": self.local_path,
            "preview_url": None,
            "cover_url": None,
            "source": self.source,
        }


class LocalMusicLibrary:
    def __init__(self, library_dir: Path | None = None) -> None:
        self._library_dir = library_dir or Path.home() / "Music" / "SanGlow"
        self._library_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self._library_dir / "library.json"
        self._tracks: list[LocalTrack] = []
        self._folders: list[str] = []
        self._load_index()

    @property
    def tracks(self) -> list[LocalTrack]:
        return self._tracks

    @property
    def folders(self) -> list[str]:
        return self._folders

    def add_folder(self, folder_path: str | Path) -> int:
        folder = Path(folder_path).resolve()
        if not folder.exists() or not folder.is_dir():
            return 0
        folder_str = str(folder)
        if folder_str in self._folders:
            return 0
        self._folders.append(folder_str)
        count = self._scan_folder(folder)
        self._save_index()
        return count

    def remove_folder(self, folder_path: str) -> None:
        folder_str = str(Path(folder_path).resolve())
        if folder_str in self._folders:
            self._folders.remove(folder_str)
            self._tracks = [t for t in self._tracks if not t.local_path.startswith(folder_str)]
            self._save_index()

    def scan_all(self) -> int:
        total = 0
        for folder_str in self._folders:
            folder = Path(folder_str)
            if folder.exists():
                total += self._scan_folder(folder)
        self._save_index()
        return total

    def search(self, query: str) -> list[LocalTrack]:
        q = query.lower()
        return [t for t in self._tracks if q in t.name.lower() or q in t.artist.lower() or q in t.album.lower()]

    def get_all_tracks(self) -> list[LocalTrack]:
        return self._tracks

    def _scan_folder(self, folder: Path) -> int:
        count = 0
        existing_paths = {t.local_path for t in self._tracks}
        for root, dirs, files in os.walk(folder):
            for fname in files:
                ext = Path(fname).suffix.lower()
                if ext not in AUDIO_EXTENSIONS:
                    continue
                fpath = str(Path(root) / fname)
                if fpath in existing_paths:
                    continue
                track = self._parse_file(Path(root), fname)
                if track:
                    self._tracks.append(track)
                    existing_paths.add(fpath)
                    count += 1
        return count

    def _parse_file(self, directory: Path, filename: str) -> LocalTrack | None:
        try:
            fpath = directory / filename
            stem = fpath.stem
            file_hash = hashlib.md5(str(fpath).encode()).hexdigest()[:16]
            name = stem
            artist = ""
            album = ""
            parts = stem.split(" - ", 1)
            if len(parts) == 2:
                artist = parts[0].strip()
                name = parts[1].strip()
            parts2 = name.split(" - ", 1)
            if len(parts2) == 2:
                if not artist:
                    artist = parts2[0].strip()
                name = parts2[1].strip()
            folder_name = directory.name
            if folder_name and folder_name != "Music":
                album = folder_name
            return LocalTrack(
                id=file_hash,
                name=name,
                artist=artist,
                album=album,
                duration_ms=0,
                local_path=str(fpath.resolve()),
            )
        except Exception:
            return None

    def _load_index(self) -> None:
        if self._index_file.exists():
            try:
                data = json.loads(self._index_file.read_text(encoding="utf-8"))
                self._folders = data.get("folders", [])
                self._tracks = [LocalTrack(**t) for t in data.get("tracks", [])]
            except Exception:
                self._tracks = []
                self._folders = []

    def _save_index(self) -> None:
        data = {
            "folders": self._folders,
            "tracks": [asdict(t) for t in self._tracks],
        }
        self._index_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
