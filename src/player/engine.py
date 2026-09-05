from __future__ import annotations

import atexit
import logging
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
import pygame
from PyQt6.QtCore import QObject, QThread, pyqtSignal

logger = logging.getLogger(__name__)

AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac", ".wma", ".opus"}


class AudioWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    ALLOWED_DOMAINS = ("spotify.com", "scdn.co", "soundcloud.com", "sndcdn.com", "ytimg.com", "youtube.com")
    BLOCKED_HOSTS = ("localhost", "127.0.0.1", "0.0.0.0", "::1", "[::1]")
    MAX_FILE_SIZE = 50 * 1024 * 1024

    def __init__(self, url: str, temp_path: str) -> None:
        super().__init__()
        self.url = url
        self.temp_path = temp_path

    def _is_allowed_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("https",):
                return False
            if not parsed.hostname:
                return False
            if parsed.hostname.lower() in self.BLOCKED_HOSTS:
                return False
            return any(parsed.hostname.endswith(d) for d in self.ALLOWED_DOMAINS)
        except Exception:
            return False

    def run(self) -> None:
        if not self._is_allowed_url(self.url):
            self.error.emit("URL not from allowed domain or not HTTPS")
            return
        try:
            with httpx.stream("GET", self.url, follow_redirects=True, timeout=30, verify=True) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")
                if not any(t in content_type.lower() for t in ("audio", "mpeg", "ogg", "wav", "octet-stream")):
                    self.error.emit("Unsupported file type")
                    return
                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > self.MAX_FILE_SIZE:
                    self.error.emit("File too large")
                    return
                downloaded = 0
                with open(self.temp_path, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        downloaded += len(chunk)
                        if downloaded > self.MAX_FILE_SIZE:
                            self.error.emit("File too large")
                            os.unlink(self.temp_path)
                            return
                        f.write(chunk)
            self.finished.emit()
        except httpx.HTTPStatusError:
            self.error.emit("Download failed")
        except Exception:
            self.error.emit("Download failed")


class MusicPlayer(QObject):
    track_changed = pyqtSignal(dict)
    playback_started = pyqtSignal()
    playback_paused = pyqtSignal()
    playback_stopped = pyqtSignal()
    speed_changed = pyqtSignal(float)

    def __init__(self) -> None:
        super().__init__()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        self._is_playing = False
        self._is_paused = False
        self._current_track: dict[str, Any] | None = None
        self._volume = 0.7
        self._speed = 1.0
        self._temp_dir = Path(tempfile.mkdtemp(prefix="sanglow_"))
        try:
            os.chmod(self._temp_dir, 0o700)
        except (OSError, PermissionError):
            pass
        self._current_file: Path | None = None
        self._active_threads: list[QThread] = []
        self._queue: list[dict[str, Any]] = []
        self._queue_index: int = -1
        self._shuffle: bool = False
        self._repeat: bool = False
        atexit.register(self.cleanup)

    @property
    def is_playing(self) -> bool:
        return self._is_playing and not self._is_paused

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = max(0.0, min(1.0, value))
        pygame.mixer.music.set_volume(self._volume)

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        self._speed = max(0.25, min(4.0, value))
        try:
            pygame.mixer.music.set_speed(self._speed)
        except (TypeError, AttributeError):
            pass
        self.speed_changed.emit(self._speed)

    @property
    def shuffle(self) -> bool:
        return self._shuffle

    @shuffle.setter
    def shuffle(self, value: bool) -> None:
        self._shuffle = value

    @property
    def repeat(self) -> bool:
        return self._repeat

    @repeat.setter
    def repeat(self, value: bool) -> None:
        self._repeat = value

    def set_queue(self, tracks: list[dict[str, Any]], start_index: int = 0) -> None:
        self._queue = tracks[:]
        self._queue_index = start_index

    def play_next(self) -> None:
        if not self._queue:
            return
        if self._repeat:
            self._queue_index = self._queue_index % len(self._queue)
        elif self._queue_index < len(self._queue) - 1:
            self._queue_index += 1
        else:
            return
        track = self._queue[self._queue_index]
        self.load_and_play(track)

    def play_previous(self) -> None:
        if not self._queue or self._queue_index <= 0:
            return
        self._queue_index -= 1
        track = self._queue[self._queue_index]
        self.load_and_play(track)

    def load_and_play(self, track: dict[str, Any]) -> None:
        local_path = track.get("local_path")
        if local_path and Path(local_path).exists():
            self.stop()
            self._current_track = track
            self._play_file(Path(local_path))
            return
        preview_url = track.get("preview_url")
        if not preview_url:
            return
        self.stop()
        self._current_track = track
        safe_id = re.sub(r"[^a-zA-Z0-9_-]", "", str(track.get("id", "unknown")))[:200] or "unknown"
        cache_file = self._temp_dir / f"{safe_id}.mp3"
        if cache_file.exists():
            self._play_file(cache_file)
        else:
            self._download_and_play(preview_url, cache_file)

    def load_local_file(self, file_path: str | Path) -> None:
        path = Path(file_path)
        if not path.exists() or path.suffix.lower() not in AUDIO_EXTENSIONS:
            return
        track = {
            "id": str(path.stem),
            "name": path.stem,
            "artist": "",
            "album": "",
            "duration_ms": 0,
            "local_path": str(path.resolve()),
        }
        self.stop()
        self._current_track = track
        self._play_file(path.resolve())

    def _download_and_play(self, url: str, target: Path) -> None:
        worker = AudioWorker(url, str(target))
        thread = QThread()
        worker.moveToThread(thread)
        worker.finished.connect(lambda: self._play_file(target))
        worker.error.connect(lambda err: logger.warning("Download error: %s", err))
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(lambda: self._cleanup_thread(thread))
        self._active_threads.append(thread)
        thread.start()

    def _cleanup_thread(self, thread: QThread) -> None:
        if thread in self._active_threads:
            self._active_threads.remove(thread)

    def _play_file(self, file_path: Path) -> None:
        if not file_path.exists():
            return
        try:
            file_size = file_path.stat().st_size
            if file_size > 50 * 1024 * 1024:
                logger.warning("File too large to play: %s bytes", file_size)
                return
            pygame.mixer.music.load(str(file_path))
            pygame.mixer.music.set_volume(self._volume)
            if self._speed != 1.0:
                try:
                    pygame.mixer.music.set_speed(self._speed)
                except (TypeError, AttributeError):
                    pass
            pygame.mixer.music.play()
            self._is_playing = True
            self._is_paused = False
            self._current_file = file_path
            self.playback_started.emit()
            if self._current_track:
                self.track_changed.emit(self._current_track)
        except pygame.error as e:
            logger.warning("Playback error: %s", e)

    def pause(self) -> None:
        if self._is_playing and not self._is_paused:
            pygame.mixer.music.pause()
            self._is_paused = True
            self.playback_paused.emit()

    def resume(self) -> None:
        if self._is_paused:
            pygame.mixer.music.unpause()
            self._is_paused = False
            self.playback_started.emit()

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self._is_playing = False
        self._is_paused = False
        self._current_track = None
        self._current_file = None
        self.playback_stopped.emit()

    def get_position(self) -> int:
        return int(pygame.mixer.music.get_pos() / 1000) if self._is_playing else 0

    def cleanup(self) -> None:
        self.stop()
        for t in self._active_threads[:]:
            try:
                t.quit()
                t.wait(1000)
            except Exception:
                pass
        self._active_threads.clear()
        pygame.mixer.quit()
        try:
            shutil.rmtree(self._temp_dir, ignore_errors=True)
        except Exception:
            pass
