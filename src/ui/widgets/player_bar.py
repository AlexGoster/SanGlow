from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QSlider, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.player.engine import MusicPlayer


class SpeedButton(QPushButton):
    def __init__(self, speed: float, parent: QWidget | None = None) -> None:
        label = f"{speed:.1f}x" if speed != int(speed) else f"{int(speed)}x"
        super().__init__(label, parent)
        self.speed = speed
        self.setFixedSize(36, 26)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #242424;
                color: #8a8580;
                border: 1px solid #3a3535;
                border-radius: 13px;
                font-size: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                color: #e8734a;
                border-color: #e8734a;
            }
            QPushButton:checked {
                background-color: #e8734a;
                color: #ffffff;
                border-color: #e8734a;
            }
        """)


class PlayerBar(QWidget):
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()

    def __init__(self, player: MusicPlayer, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._player = player
        self.setObjectName("playerBar")
        self.setFixedHeight(90)
        self._speed_buttons: list[SpeedButton] = []
        self._setup_ui()
        self._player.playback_started.connect(lambda: self._play_btn.setText("\u23F8"))
        self._player.playback_paused.connect(lambda: self._play_btn.setText("\u25B6"))
        self._player.playback_stopped.connect(self._on_stopped)
        self._player.track_changed.connect(self._on_track_changed)

    def _setup_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 8, 20, 6)
        main.setSpacing(0)

        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        info = QVBoxLayout()
        info.setSpacing(2)
        self._title_label = QLabel("No track playing")
        self._title_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #e0d6cc; background: transparent;")
        self._artist_label = QLabel("")
        self._artist_label.setStyleSheet("color: #8a8580; font-size: 11px; background: transparent;")
        info.addWidget(self._title_label)
        info.addWidget(self._artist_label)
        info.addStretch()
        top_row.addLayout(info, stretch=2)

        controls = QHBoxLayout()
        controls.setSpacing(20)
        controls.setAlignment(Qt.AlignmentFlag.AlignCenter)

        prev_btn = QPushButton("\u23EE")
        prev_btn.setFixedSize(32, 32)
        prev_btn.setStyleSheet("QPushButton { font-size: 14px; color: #8a8580; background: transparent; border: none; } QPushButton:hover { color: #e8734a; }")
        prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        prev_btn.clicked.connect(self.prev_clicked.emit)

        self._play_btn = QPushButton("\u25B6")
        self._play_btn.setObjectName("playButton")
        self._play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._play_btn.clicked.connect(self._toggle_play)

        next_btn = QPushButton("\u23ED")
        next_btn.setFixedSize(32, 32)
        next_btn.setStyleSheet("QPushButton { font-size: 14px; color: #8a8580; background: transparent; border: none; } QPushButton:hover { color: #e8734a; }")
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.clicked.connect(self.next_clicked.emit)

        controls.addWidget(prev_btn)
        controls.addWidget(self._play_btn)
        controls.addWidget(next_btn)
        top_row.addLayout(controls, stretch=1)

        vol_layout = QHBoxLayout()
        vol_layout.setSpacing(6)
        vol_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        vol_icon = QLabel("\U0001F50A")
        vol_icon.setFixedSize(20, 20)
        vol_icon.setStyleSheet("font-size: 11px; color: #5a5550; background: transparent;")
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setFixedWidth(90)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(70)
        self._volume_slider.valueChanged.connect(lambda v: setattr(self._player, 'volume', v / 100.0))
        vol_layout.addWidget(vol_icon)
        vol_layout.addWidget(self._volume_slider)
        top_row.addLayout(vol_layout)

        main.addLayout(top_row)

        speed_row = QHBoxLayout()
        speed_row.setSpacing(6)
        speed_row.setContentsMargins(0, 6, 0, 0)

        for s in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
            btn = SpeedButton(s)
            btn.clicked.connect(lambda checked, b=btn: self._set_speed(b.speed))
            if s == 1.0:
                btn.setChecked(True)
            self._speed_buttons.append(btn)
            speed_row.addWidget(btn)

        speed_row.addSpacing(8)

        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setFixedWidth(100)
        self._speed_slider.setRange(25, 200)
        self._speed_slider.setValue(100)
        self._speed_slider.valueChanged.connect(self._on_speed_slider)
        speed_row.addWidget(self._speed_slider)

        self._speed_value = QLabel("1.0x")
        self._speed_value.setFixedWidth(30)
        self._speed_value.setStyleSheet("font-size: 10px; color: #e8734a; font-weight: 600; background: transparent;")
        speed_row.addWidget(self._speed_value)

        speed_row.addStretch()
        main.addLayout(speed_row)

    def _set_speed(self, speed: float) -> None:
        self._player.speed = speed
        self._speed_slider.blockSignals(True)
        self._speed_slider.setValue(int(speed * 100))
        self._speed_slider.blockSignals(False)
        self._speed_value.setText(f"{speed:.1f}x")
        for btn in self._speed_buttons:
            btn.setChecked(btn.speed == speed)

    def _on_speed_slider(self, value: int) -> None:
        speed = value / 100.0
        speed = round(speed * 4) / 4
        speed = max(0.25, min(2.0, speed))
        self._player.speed = speed
        self._speed_value.setText(f"{speed:.1f}x")
        for btn in self._speed_buttons:
            btn.setChecked(abs(btn.speed - speed) < 0.01)

    def _toggle_play(self) -> None:
        if self._player.is_playing:
            self._player.pause()
        elif self._player.is_paused:
            self._player.resume()

    def _on_track_changed(self, track: dict) -> None:
        self._title_label.setText(track.get("name", "Unknown"))
        self._artist_label.setText(track.get("artist", "Unknown"))

    def _on_stopped(self) -> None:
        self._play_btn.setText("\u25B6")
        self._title_label.setText("No track playing")
        self._artist_label.setText("")
