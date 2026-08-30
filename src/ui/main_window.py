from __future__ import annotations

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QStackedWidget,
    QFrame, QTabWidget, QScrollArea, QGridLayout, QTextEdit,
    QMenu, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.spotify.client import SpotifyClient, Track
from src.player.engine import MusicPlayer
from src.ui.widgets.player_bar import PlayerBar
from src.models.database import get_db_session
from src.social.service import SocialService


class TrackCard(QFrame):
    like_toggled = pyqtSignal(dict)
    favorite_toggled = pyqtSignal(dict)

    def __init__(self, track: Track, index: int, user_id: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.track = track
        self.user_id = user_id
        self._is_liked = False
        self._is_fav = False
        self.setObjectName("card")
        self.setFixedHeight(56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        num = QLabel(f"{index + 1}")
        num.setFixedWidth(24)
        num.setStyleSheet("color: #5a5550; font-size: 12px; background: transparent;")
        layout.addWidget(num)

        info = QVBoxLayout()
        info.setSpacing(1)
        title = QLabel(track.name)
        title.setObjectName("trackTitle")
        title.setMaximumWidth(300)
        titleElide = title.fontMetrics().elidedText(track.name, Qt.TextElideMode.ElideRight, 300)
        title.setText(titleElide)
        artist = QLabel(track.artist)
        artist.setObjectName("trackArtist")
        artistElide = artist.fontMetrics().elidedText(track.artist, Qt.TextElideMode.ElideRight, 300)
        artist.setText(artistElide)
        info.addWidget(title)
        info.addWidget(artist)
        layout.addLayout(info, stretch=1)

        ms = track.duration_ms
        mins, secs = divmod(ms // 1000, 60)
        duration = QLabel(f"{mins}:{secs:02d}")
        duration.setStyleSheet("color: #5a5550; font-size: 11px; background: transparent;")
        layout.addWidget(duration)

        self._like_btn = QPushButton("\u2661")
        self._like_btn.setObjectName("likeButton")
        self._like_btn.setFixedSize(28, 28)
        self._like_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._like_btn.clicked.connect(self._toggle_like)
        layout.addWidget(self._like_btn)

        self._fav_btn = QPushButton("\u2606")
        self._fav_btn.setObjectName("likeButton")
        self._fav_btn.setFixedSize(28, 28)
        self._fav_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._fav_btn.clicked.connect(self._toggle_fav)
        layout.addWidget(self._fav_btn)

    def _toggle_like(self):
        self._is_liked = not self._is_liked
        self._like_btn.setText("\u2665" if self._is_liked else "\u2661")
        self.like_toggled.emit({"id": self.track.id, "liked": self._is_liked})

    def _toggle_fav(self):
        self._is_fav = not self._is_fav
        self._fav_btn.setText("\u2605" if self._is_fav else "\u2606")
        self.favorite_toggled.emit({"id": self.track.id, "fav": self._is_fav})

    def set_liked(self, v: bool):
        self._is_liked = v
        self._like_btn.setText("\u2665" if v else "\u2661")

    def set_fav(self, v: bool):
        self._is_fav = v
        self._fav_btn.setText("\u2605" if v else "\u2606")


class CommentWidget(QFrame):
    def __init__(self, comment: dict, current_user_id: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("commentItem")
        self.setFixedHeight(60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        avatar = QLabel(comment.get("display_name", "?")[0].upper())
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("background-color: #e8734a; color: #ffffff; border-radius: 16px; font-size: 13px; font-weight: 700;")
        layout.addWidget(avatar)

        col = QVBoxLayout()
        col.setSpacing(1)
        header = QHBoxLayout()
        user = QLabel(comment.get("display_name", "Unknown"))
        user.setObjectName("commentUser")
        header.addWidget(user)
        time_str = comment.get("created_at", "")
        try:
            dt = datetime.fromisoformat(time_str)
            time_str = dt.strftime("%d %b, %H:%M")
        except Exception:
            pass
        ts = QLabel(time_str)
        ts.setObjectName("commentTime")
        header.addWidget(ts)
        header.addStretch()
        col.addLayout(header)
        text = QLabel(comment.get("text", ""))
        text.setObjectName("commentText")
        text.setWordWrap(True)
        col.addWidget(text)
        layout.addLayout(col, stretch=1)


class WaveCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, wave: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.wave_id = wave.get("id", "")
        self.setObjectName("waveCard")
        self.setFixedHeight(72)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        icon = QLabel("\u26A1")
        icon.setFixedSize(48, 48)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("background-color: #e8734a; color: #ffffff; border-radius: 24px; font-size: 20px;")
        layout.addWidget(icon)

        col = QVBoxLayout()
        col.setSpacing(2)
        name = QLabel(wave.get("name", "Wave"))
        name.setStyleSheet("font-size: 14px; font-weight: 600; color: #e0d6cc; background: transparent;")
        col.addWidget(name)
        tc = wave.get("track_count", 0)
        tracks_label = QLabel(f"{tc} tracks")
        tracks_label.setStyleSheet("font-size: 11px; color: #8a8580; background: transparent;")
        col.addWidget(tracks_label)
        layout.addLayout(col, stretch=1)

        self.mousePressEvent = lambda e: self.clicked.emit(self.wave_id)


class MainWindow(QWidget):
    def __init__(self, user_data: dict, spotify_client: SpotifyClient | None = None) -> None:
        super().__init__()
        self._user_data = user_data
        self._user_id = user_data.get("id", "")
        self._spotify = spotify_client
        self._player = MusicPlayer()
        self._current_track_data: dict | None = None
        self.setWindowTitle("SanGlow")
        self.setMinimumSize(1000, 700)
        self.resize(1100, 750)
        self._setup_ui()
        self._player.track_changed.connect(self._on_track_changed)

    def _setup_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(12, 20, 12, 16)
        sb.setSpacing(4)

        logo = QLabel("SanGlow")
        logo.setStyleSheet("font-size: 20px; font-weight: 700; color: #e8734a; padding: 4px 8px;")
        sb.addWidget(logo)
        sb.addSpacing(20)

        self._nav_buttons = []
        nav_items = [("\U0001F3E0", "Home", 0), ("\U0001F50D", "Search", 1), ("\U0001F4DA", "Library", 2), ("\u26A1", "My Waves", 3)]
        for icon, label, idx in nav_items:
            btn = QPushButton(f"  {icon}    {label}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            sb.addWidget(btn)
            self._nav_buttons.append(btn)
        self._nav_buttons[0].setChecked(True)

        sb.addStretch()

        profile = QFrame()
        profile.setStyleSheet("QFrame { background: #242424; border-radius: 10px; }")
        profile.setFixedHeight(52)
        pl = QHBoxLayout(profile)
        pl.setContentsMargins(10, 8, 10, 8)
        pl.setSpacing(10)
        avatar = QLabel(self._user_data.get("username", "U")[0].upper())
        avatar.setFixedSize(34, 34)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("background-color: #e8734a; color: #ffffff; border-radius: 17px; font-size: 14px; font-weight: 700;")
        pl.addWidget(avatar)
        name = QLabel(self._user_data.get("display_name", self._user_data.get("username", "")))
        name.setStyleSheet("font-size: 12px; font-weight: 600; color: #e0d6cc; background: transparent;")
        pl.addWidget(name)
        sb.addWidget(profile)

        main_layout.addWidget(sidebar)

        content_area = QVBoxLayout()
        content_area.setContentsMargins(0, 0, 0, 0)
        content_area.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet("background-color: #1a1a1a;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("What do you want to listen to?")
        self._search_input.setFixedWidth(420)
        self._search_input.setFixedHeight(40)
        self._search_input.returnPressed.connect(self._perform_search)
        h_layout.addWidget(self._search_input)
        h_layout.addStretch()
        content_area.addWidget(header)

        self._content_stack = QStackedWidget()
        self._content_stack.addWidget(self._create_home_page())
        self._content_stack.addWidget(self._create_search_page())
        self._content_stack.addWidget(self._create_library_page())
        self._content_stack.addWidget(self._create_waves_page())
        content_area.addWidget(self._content_stack, stretch=1)

        content_area.addWidget(PlayerBar(self._player))

        content_widget = QWidget()
        content_widget.setLayout(content_area)
        main_layout.addWidget(content_widget, stretch=4)

    def _switch_page(self, idx: int) -> None:
        self._content_stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == idx)

    def _create_home_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 16)
        layout.setSpacing(20)

        greeting = QLabel(f"Good evening, {self._user_data.get('display_name', 'User')}")
        greeting.setObjectName("sectionTitle")
        layout.addWidget(greeting)

        quick_grid = QGridLayout()
        quick_grid.setSpacing(12)
        labels = ["Recently Played", "Your Top Tracks", "Liked Songs", "Discover Weekly", "Release Radar", "Daily Mix"]
        for i, lbl_text in enumerate(labels):
            card = QFrame()
            card.setFixedHeight(64)
            card.setStyleSheet("QFrame { background: #242424; border-radius: 10px; } QFrame:hover { background: #2a2a2a; }")
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(14, 0, 14, 0)
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #e0d6cc; background: transparent;")
            cl.addWidget(lbl)
            quick_grid.addWidget(card, i // 3, i % 3)
        layout.addLayout(quick_grid)

        if self._spotify:
            layout.addWidget(self._section("Recently Played"))
            self._recent_list = QListWidget()
            self._recent_list.setMaximumHeight(180)
            layout.addWidget(self._recent_list)

            layout.addWidget(self._section("Your Top Tracks"))
            self._top_tracks_list = QListWidget()
            self._top_tracks_list.setMaximumHeight(180)
            layout.addWidget(self._top_tracks_list)

        layout.addStretch()
        return page

    def _create_search_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 16)

        self._results_list = QListWidget()
        self._results_list.currentRowChanged.connect(self._on_track_selected)
        layout.addWidget(self._results_list)
        return page

    def _create_library_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 16)

        title = QLabel("Your Library")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        tabs = QTabWidget()
        self._playlists_list = QListWidget()
        tabs.addTab(self._playlists_list, "Playlists")
        self._favorites_list = QListWidget()
        tabs.addTab(self._favorites_list, "Favorites")
        layout.addWidget(tabs)
        return page

    def _create_waves_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 16)
        layout.setSpacing(16)

        top = QHBoxLayout()
        title = QLabel("My Waves")
        title.setObjectName("sectionTitle")
        top.addWidget(title)
        top.addStretch()
        create_btn = QPushButton("+ New Wave")
        create_btn.setObjectName("primaryButton")
        create_btn.setFixedHeight(36)
        create_btn.clicked.connect(self._create_wave)
        top.addWidget(create_btn)
        layout.addLayout(top)

        self._waves_list = QListWidget()
        self._waves_list.currentRowChanged.connect(self._on_wave_selected)
        layout.addWidget(self._waves_list)

        self._wave_tracks_list = QListWidget()
        layout.addWidget(self._wave_tracks_list)
        return page

    def _section(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("sectionTitle")
        return lbl

    def _perform_search(self) -> None:
        query = self._search_input.text().strip()
        if not query or not self._spotify:
            return
        results = self._spotify.search(query, search_type="track")
        self._results_list.clear()
        for track in results.get("tracks", []):
            item = QListWidgetItem()
            widget = TrackCard(track, self._results_list.count(), self._user_id)
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, track)
            self._results_list.addItem(item)
            self._results_list.setItemWidget(item, widget)

    def _on_track_selected(self, row: int) -> None:
        item = self._results_list.item(row)
        if item:
            track = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(track, Track):
                data = {"id": track.id, "name": track.name, "artist": track.artist,
                        "album": track.album, "preview_url": track.preview_url}
                self._current_track_data = data
                self._player.load_and_play(data)

    def _on_track_changed(self, track: dict) -> None:
        self._current_track_data = track

    def _create_wave(self) -> None:
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "New Wave", "Wave name:")
        if ok and name.strip():
            with get_db_session() as db:
                svc = SocialService(db)
                svc.create_wave(self._user_id, name.strip())
            self._load_waves()

    def _on_wave_selected(self, row: int) -> None:
        item = self._waves_list.item(row)
        if item:
            wave_id = item.data(Qt.ItemDataRole.UserRole)
            if wave_id:
                with get_db_session() as db:
                    svc = SocialService(db)
                    tracks = svc.get_wave_tracks(wave_id)
                self._wave_tracks_list.clear()
                for t in tracks:
                    self._wave_tracks_list.addItem(f"{t['name']} — {t['artist']}")

    def _load_waves(self) -> None:
        with get_db_session() as db:
            svc = SocialService(db)
            waves = svc.get_waves(self._user_id)
        self._waves_list.clear()
        for w in waves:
            item = QListWidgetItem(f"\u26A1  {w['name']}  ({w['track_count']} tracks)")
            item.setData(Qt.ItemDataRole.UserRole, w["id"])
            self._waves_list.addItem(item)

    def load_data(self) -> None:
        if not self._spotify:
            return
        try:
            for track in self._spotify.get_recently_played(limit=10):
                self._recent_list.addItem(f"{track.name} — {track.artist}")
            for track in self._spotify.get_top_tracks(limit=10):
                self._top_tracks_list.addItem(f"{track.name} — {track.artist}")
            for pl in self._spotify.get_user_playlists(limit=50):
                self._playlists_list.addItem(f"{pl.name}  ({pl.track_count} tracks)")
        except Exception:
            pass
        self._load_waves()

    def closeEvent(self, event) -> None:
        self._player.cleanup()
        event.accept()
