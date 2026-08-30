from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import httpx
import pygame
from PyQt6.QtCore import QObject, QThread, pyqtSignal


class AudioWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url: str, temp_path: str) -> None:
        super().__init__()
        self.url = url
        self.temp_path = temp_path

    def run(self) -> None:
        try:
            with httpx.stream("GET", self.url, follow_redirects=True) as response:
                response.raise_for_status()
                with open(self.temp_path, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


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
        self._current_file: Path | None = None

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

    def load_and_play(self, track: dict[str, Any]) -> None:
        preview_url = track.get("preview_url")
        if not preview_url:
            return
        self.stop()
        self._current_track = track
        cache_file = self._temp_dir / f"{track.get('id', 'unknown')}.mp3"
        if cache_file.exists():
            self._play_file(cache_file)
        else:
            self._download_and_play(preview_url, cache_file)

    def _download_and_play(self, url: str, target: Path) -> None:
        worker = AudioWorker(url, str(target))
        thread = QThread()
        worker.moveToThread(thread)
        worker.finished.connect(lambda: self._play_file(target))
        worker.error.connect(lambda err: print(f"Download error: {err}"))
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.start()

    def _play_file(self, file_path: Path) -> None:
        try:
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
            print(f"Playback error: {e}")

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
        pygame.mixer.quit()
        import shutil
        shutil.rmtree(self._temp_dir, ignore_errors=True)
