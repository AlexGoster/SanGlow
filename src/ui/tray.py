from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction
from PyQt6.QtCore import QObject, pyqtSignal

if TYPE_CHECKING:
    from src.player.engine import MusicPlayer

logger = logging.getLogger(__name__)


def _create_tray_icon() -> QIcon:
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QColor("#e8734a"))
    painter.setPen(QColor("#e8734a"))
    painter.drawEllipse(2, 2, size - 4, size - 4)

    painter.setPen(QColor("#ffffff"))
    font = QFont("Segoe UI", 24, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), 0x0084, "S")

    painter.end()
    return QIcon(pixmap)


class TrayIcon(QObject):
    play_pause_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    show_clicked = pyqtSignal()
    quit_clicked = pyqtSignal()

    def __init__(self, player: MusicPlayer, parent=None) -> None:
        super().__init__(parent)
        self._player = player
        self._tray = QSystemTrayIcon()
        self._tray.setIcon(_create_tray_icon())
        self._tray.setToolTip("SanGlow")
        self._menu = QMenu()
        self._setup_menu()
        self._tray.setContextMenu(self._menu)
        self._tray.activated.connect(self._on_activated)
        self._player.playback_started.connect(lambda: self._update_tooltip("Playing"))
        self._player.playback_paused.connect(lambda: self._update_tooltip("Paused"))
        self._player.playback_stopped.connect(lambda: self._update_tooltip("SanGlow"))
        self._player.track_changed.connect(self._on_track_changed)

    def _setup_menu(self) -> None:
        self._play_action = QAction("Play", self._menu)
        self._play_action.triggered.connect(self.play_pause_clicked.emit)
        self._menu.addAction(self._play_action)

        self._menu.addSeparator()

        prev_action = QAction("Previous", self._menu)
        prev_action.triggered.connect(self.prev_clicked.emit)
        self._menu.addAction(prev_action)

        next_action = QAction("Next", self._menu)
        next_action.triggered.connect(self.next_clicked.emit)
        self._menu.addAction(next_action)

        stop_action = QAction("Stop", self._menu)
        stop_action.triggered.connect(self.stop_clicked.emit)
        self._menu.addAction(stop_action)

        self._menu.addSeparator()

        show_action = QAction("Show SanGlow", self._menu)
        show_action.triggered.connect(self.show_clicked.emit)
        self._menu.addAction(show_action)

        self._menu.addSeparator()

        quit_action = QAction("Quit", self._menu)
        quit_action.triggered.connect(self.quit_clicked.emit)
        self._menu.addAction(quit_action)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_clicked.emit()

    def _on_track_changed(self, track: dict) -> None:
        name = track.get("name", "")
        artist = track.get("artist", "")
        self._tray.setToolTip(f"{name} - {artist}")
        self._play_action.setText("Pause" if self._player.is_playing else "Play")

    def _update_tooltip(self, text: str) -> None:
        if self._player._current_track:
            name = self._player._current_track.get("name", "")
            artist = self._player._current_track.get("artist", "")
            self._tray.setToolTip(f"{text}: {name} - {artist}")
        else:
            self._tray.setToolTip(f"SanGlow - {text}")

    def show(self) -> None:
        self._tray.show()

    def hide(self) -> None:
        self._tray.hide()

    def is_visible(self) -> bool:
        return self._tray.isVisible()
