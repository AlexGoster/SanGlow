from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QSlider, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from src.player.engine import MusicPlayer
from src.i18n import t


class PlayerBar(QWidget):
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()

    def __init__(self, player: MusicPlayer, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._player = player
        self.setObjectName("playerBar")
        self.setFixedHeight(80)
        self._setup_ui()
        self._player.playback_started.connect(self._on_play)
        self._player.playback_paused.connect(self._on_pause)
        self._player.playback_stopped.connect(self._on_stopped)
        self._player.track_changed.connect(self._on_track_changed)

    def _setup_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(16, 0, 16, 0)
        main.setSpacing(16)

        left = QHBoxLayout()
        left.setSpacing(12)
        left.setContentsMargins(0, 0, 0, 0)

        self._cover = QLabel("\u266B")
        self._cover.setFixedSize(56, 56)
        self._cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover.setStyleSheet("background: #252525; color: #e8734a; border-radius: 4px; font-size: 20px;")
        left.addWidget(self._cover)

        info = QVBoxLayout()
        info.setSpacing(2)
        info.setContentsMargins(0, 0, 0, 0)
        self._title = QLabel(t("no_track_playing"))
        self._title.setStyleSheet("font-size: 14px; font-weight: 600; color: #ffffff; background: transparent;")
        self._title.setMaximumWidth(200)
        self._artist = QLabel("")
        self._artist.setStyleSheet("font-size: 12px; color: #a09888; background: transparent;")
        self._artist.setMaximumWidth(200)
        info.addWidget(self._title)
        info.addWidget(self._artist)
        info.addStretch()
        left.addLayout(info)

        like_btn = QPushButton("\u2661")
        like_btn.setFixedSize(28, 28)
        like_btn.setStyleSheet("QPushButton { font-size: 16px; color: #a09888; background: transparent; border: none; } QPushButton:hover { color: #e8734a; }")
        like_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        left.addWidget(like_btn)

        main.addLayout(left, stretch=2)

        center = QVBoxLayout()
        center.setSpacing(4)
        center.setContentsMargins(0, 0, 0, 0)

        controls = QHBoxLayout()
        controls.setSpacing(16)
        controls.setAlignment(Qt.AlignmentFlag.AlignCenter)

        shuffle_btn = QPushButton("\u2684")
        shuffle_btn.setFixedSize(28, 28)
        shuffle_btn.setStyleSheet("QPushButton { font-size: 12px; color: #a09888; background: transparent; border: none; } QPushButton:hover { color: #ffffff; }")
        shuffle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        controls.addWidget(shuffle_btn)

        prev_btn = QPushButton("\u23EE")
        prev_btn.setFixedSize(32, 32)
        prev_btn.setStyleSheet("QPushButton { font-size: 14px; color: #a09888; background: transparent; border: none; } QPushButton:hover { color: #ffffff; }")
        prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        prev_btn.clicked.connect(self.prev_clicked.emit)
        controls.addWidget(prev_btn)

        self._play_btn = QPushButton("\u25B6")
        self._play_btn.setObjectName("playButton")
        self._play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._play_btn.clicked.connect(self._toggle_play)
        controls.addWidget(self._play_btn)

        next_btn = QPushButton("\u23ED")
        next_btn.setFixedSize(32, 32)
        next_btn.setStyleSheet("QPushButton { font-size: 14px; color: #a09888; background: transparent; border: none; } QPushButton:hover { color: #ffffff; }")
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.clicked.connect(self.next_clicked.emit)
        controls.addWidget(next_btn)

        repeat_btn = QPushButton("\u27F3")
        repeat_btn.setFixedSize(28, 28)
        repeat_btn.setStyleSheet("QPushButton { font-size: 12px; color: #a09888; background: transparent; border: none; } QPushButton:hover { color: #ffffff; }")
        repeat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        controls.addWidget(repeat_btn)

        center.addLayout(controls)

        progress_row = QHBoxLayout()
        progress_row.setSpacing(8)
        self._time_label = QLabel("0:00")
        self._time_label.setStyleSheet("font-size: 11px; color: #a09888; background: transparent;")
        self._time_label.setFixedWidth(36)
        progress_row.addWidget(self._time_label)

        self._progress = QSlider(Qt.Orientation.Horizontal)
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setStyleSheet("""
            QSlider::groove:horizontal { height: 4px; background: #444444; border-radius: 2px; }
            QSlider::handle:horizontal { background: #ffffff; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
            QSlider::handle:horizontal:hover { background: #ffffff; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }
            QSlider::sub-page:horizontal { background: #a09888; border-radius: 2px; }
            QSlider:hover::sub-page:horizontal { background: #e8734a; }
        """)
        progress_row.addWidget(self._progress, stretch=1)

        self._duration_label = QLabel("0:00")
        self._duration_label.setStyleSheet("font-size: 11px; color: #a09888; background: transparent;")
        self._duration_label.setFixedWidth(36)
        progress_row.addWidget(self._duration_label)

        center.addLayout(progress_row)
        main.addLayout(center, stretch=4)

        right = QHBoxLayout()
        right.setSpacing(8)
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        queue_btn = QPushButton("\u2630")
        queue_btn.setFixedSize(28, 28)
        queue_btn.setStyleSheet("QPushButton { font-size: 14px; color: #a09888; background: transparent; border: none; } QPushButton:hover { color: #ffffff; }")
        queue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        right.addWidget(queue_btn)

        vol_icon = QLabel("\U0001F50A")
        vol_icon.setFixedSize(20, 20)
        vol_icon.setStyleSheet("font-size: 12px; color: #a09888; background: transparent;")
        right.addWidget(vol_icon)

        self._volume = QSlider(Qt.Orientation.Horizontal)
        self._volume.setFixedWidth(100)
        self._volume.setRange(0, 100)
        self._volume.setValue(70)
        self._volume.setStyleSheet("""
            QSlider::groove:horizontal { height: 4px; background: #444444; border-radius: 2px; }
            QSlider::handle:horizontal { background: #ffffff; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
            QSlider::handle:horizontal:hover { background: #ffffff; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }
            QSlider::sub-page:horizontal { background: #e8734a; border-radius: 2px; }
        """)
        self._volume.valueChanged.connect(lambda v: setattr(self._player, 'volume', v / 100.0))
        right.addWidget(self._volume)

        main.addLayout(right, stretch=1)

    def _toggle_play(self) -> None:
        if self._player.is_playing:
            self._player.pause()
        elif self._player.is_paused:
            self._player.resume()

    def _on_play(self) -> None:
        self._play_btn.setText("\u23F8")

    def _on_pause(self) -> None:
        self._play_btn.setText("\u25B6")

    def _on_track_changed(self, track: dict) -> None:
        self._title.setText(track.get("name", "Unknown"))
        self._artist.setText(track.get("artist", ""))

    def _on_stopped(self) -> None:
        self._play_btn.setText("\u25B6")
        self._title.setText(t("no_track_playing"))
        self._artist.setText("")
