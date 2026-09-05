from __future__ import annotations

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QStackedWidget,
    QFrame, QTabWidget, QScrollArea, QGridLayout, QTextEdit,
    QMenu, QMessageBox, QDialog, QFormLayout,
    QComboBox, QCheckBox, QSizePolicy, QSpacerItem,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QSystemTrayIcon

from src.spotify.client import SpotifyClient, Track
from src.player.engine import MusicPlayer
from src.ui.widgets.player_bar import PlayerBar
from src.ui.greeting import get_greeting, get_suggested_playlists, get_time_of_day
from src.models.database import get_db_session
from src.social.service import SocialService
from src.ui.tray import TrayIcon
from src.i18n import t, load_translations, get_available_languages


_SEARCH_CATEGORIES = [
    {"name": "Pop", "color": "#E13300", "icon": "\U0001F3B5"},
    {"name": "Hip-Hop", "color": "#BA5D07", "icon": "\U0001F3B6"},
    {"name": "Rock", "color": "#E91429", "icon": "\U0001F3B8"},
    {"name": "Electronic", "color": "#1E3264", "icon": "\U0001F9E0"},
    {"name": "Jazz", "color": "#477D95", "icon": "\U0001F3B7"},
    {"name": "Classical", "color": "#7D4B32", "icon": "\U0001F3B9"},
    {"name": "R&B", "color": "#DC148C", "icon": "\U0001F3A4"},
    {"name": "Indie", "color": "#608108", "icon": "\U0001F33F"},
    {"name": "Metal", "color": "#1E3264", "icon": "\u2694\uFE0F"},
    {"name": "Country", "color": "#E1118B", "icon": "\U0001F33E"},
    {"name": "Latin", "color": "#E1118B", "icon": "\U0001F525"},
    {"name": "Podcasts", "color": "#006450", "icon": "\U0001F4FA"},
]


class TrackRow(QFrame):
    clicked = pyqtSignal(dict)
    like_toggled = pyqtSignal(dict)

    def __init__(self, track: Track, index: int, user_id: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.track = track
        self._is_liked = False
        self.setObjectName("trackRow")
        self.setFixedHeight(56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(16)

        num = QLabel(f"{index + 1}")
        num.setFixedWidth(24)
        num.setStyleSheet("color: #a0a0a0; font-size: 14px; background: transparent;")
        layout.addWidget(num)

        cover = QLabel("\u266B")
        cover.setFixedSize(40, 40)
        cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover.setStyleSheet("background: #282828; color: #e8734a; border-radius: 4px; font-size: 16px;")
        layout.addWidget(cover)

        info = QVBoxLayout()
        info.setSpacing(2)
        title = QLabel(track.name)
        title.setObjectName("trackTitle")
        title.setMaximumWidth(320)
        title.setText(title.fontMetrics().elidedText(track.name, Qt.TextElideMode.ElideRight, 320))
        artist = QLabel(track.artist)
        artist.setObjectName("trackArtist")
        artist.setMaximumWidth(320)
        artist.setText(artist.fontMetrics().elidedText(track.artist, Qt.TextElideMode.ElideRight, 320))
        info.addWidget(title)
        info.addWidget(artist)
        layout.addLayout(info, stretch=1)

        album = QLabel(track.album if hasattr(track, 'album') else "")
        album.setStyleSheet("color: #a0a0a0; font-size: 13px; background: transparent;")
        album.setMaximumWidth(200)
        layout.addWidget(album)

        ms = track.duration_ms
        mins, secs = divmod(ms // 1000, 60)
        duration = QLabel(f"{mins}:{secs:02d}")
        duration.setStyleSheet("color: #a0a0a0; font-size: 13px; background: transparent;")
        layout.addWidget(duration)

        self._like_btn = QPushButton("\u2661")
        self._like_btn.setObjectName("likeButton")
        self._like_btn.setFixedSize(28, 28)
        self._like_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._like_btn.clicked.connect(self._toggle_like)
        layout.addWidget(self._like_btn)

    def _toggle_like(self):
        self._is_liked = not self._is_liked
        self._like_btn.setText("\u2665" if self._is_liked else "\u2661")
        self.like_toggled.emit({"id": self.track.id, "liked": self._is_liked})

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            data = {"id": self.track.id, "name": self.track.name, "artist": self.track.artist,
                    "album": getattr(self.track, 'album', ''), "preview_url": getattr(self.track, 'preview_url', None)}
            self.clicked.emit(data)


class CategoryCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, cat: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cat = cat
        self.setFixedSize(180, 180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{
                background: {cat['color']};
                border-radius: 12px;
            }}
            QFrame:hover {{
                background: {cat['color']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        icon = QLabel(cat.get("icon", "\U0001F3B5"))
        icon.setStyleSheet("font-size: 32px; background: transparent;")
        layout.addWidget(icon)

        name = QLabel(cat["name"])
        name.setStyleSheet("font-size: 16px; font-weight: 700; color: #ffffff; background: transparent;")
        layout.addWidget(name)

        layout.addStretch()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._cat)


class PlaylistCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, playlist: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.playlist = playlist
        self.setObjectName("playlistCard")
        self.setFixedHeight(220)
        self.setFixedWidth(180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 16)
        layout.setSpacing(10)

        cover = QLabel("\u266B")
        cover.setFixedSize(156, 156)
        cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover.setStyleSheet("background: #282828; color: #e8734a; border-radius: 8px; font-size: 40px;")
        layout.addWidget(cover)

        name = QLabel(playlist.get("name", "Playlist"))
        name.setStyleSheet("font-size: 14px; font-weight: 600; color: #ffffff; background: transparent;")
        name.setText(name.fontMetrics().elidedText(playlist.get("name", ""), Qt.TextElideMode.ElideRight, 160))
        layout.addWidget(name)

        desc = QLabel(playlist.get("description", ""))
        desc.setStyleSheet("font-size: 12px; color: #a0a0a0; background: transparent;")
        desc.setMaximumWidth(160)
        desc.setText(desc.fontMetrics().elidedText(playlist.get("description", ""), Qt.TextElideMode.ElideRight, 160))
        layout.addWidget(desc)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.playlist)


class ProfileDialog(QDialog):
    def __init__(self, user_data: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._user_data = user_data
        self.setWindowTitle(f"SanGlow - {t('profile_settings')}")
        self.setMinimumWidth(420)
        self.setStyleSheet("""
            QDialog { background: #1e1e1e; color: #e0d6cc; }
            QLabel { color: #e0d6cc; font-size: 13px; }
            QLineEdit { background: #2a2a2a; color: #e0d6cc; border: 1px solid #3a3a3a;
                         border-radius: 6px; padding: 8px 12px; font-size: 13px; }
            QLineEdit:focus { border-color: #e8734a; }
            QComboBox { background: #2a2a2a; color: #e0d6cc; border: 1px solid #3a3a3a;
                         border-radius: 6px; padding: 8px 12px; font-size: 13px; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background: #2a2a2a; color: #e0d6cc; selection-background-color: #e8734a; }
            QCheckBox { color: #e0d6cc; font-size: 13px; spacing: 8px; }
            QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px;
                                   border: 2px solid #3a3a3a; background: #2a2a2a; }
            QCheckBox::indicator:checked { background: #e8734a; border-color: #e8734a; }
            QPushButton { background: #e8734a; color: #ffffff; border: none; border-radius: 6px;
                          padding: 8px 20px; font-size: 13px; font-weight: 600; }
            QPushButton:hover { background: #d4633a; }
            QPushButton#cancelBtn { background: #3a3a3a; color: #e0d6cc; }
            QPushButton#cancelBtn:hover { background: #4a4a4a; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel(t("profile_settings"))
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #e8734a; margin-bottom: 8px;")
        layout.addWidget(title)

        avatar_row = QHBoxLayout()
        avatar_label = QLabel(user_data.get("username", "U")[0].upper())
        avatar_label.setFixedSize(56, 56)
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_label.setStyleSheet("background-color: #e8734a; color: #ffffff; border-radius: 28px; font-size: 22px; font-weight: 700;")
        avatar_row.addWidget(avatar_label)
        avatar_info = QVBoxLayout()
        avatar_info.setSpacing(2)
        name_lbl = QLabel(user_data.get("display_name", user_data.get("username", "")))
        name_lbl.setStyleSheet("font-size: 16px; font-weight: 600; color: #e0d6cc;")
        email_lbl = QLabel(user_data.get("email", ""))
        email_lbl.setStyleSheet("font-size: 12px; color: #888;")
        avatar_info.addWidget(name_lbl)
        avatar_info.addWidget(email_lbl)
        avatar_info.addStretch()
        avatar_row.addLayout(avatar_info)
        avatar_row.addStretch()
        layout.addLayout(avatar_row)

        form = QFormLayout()
        form.setSpacing(12)

        self._display_name = QLineEdit(user_data.get("display_name", ""))
        self._display_name.setPlaceholderText(t("display_name"))
        form.addRow(t("display_name"), self._display_name)

        self._email = QLineEdit(user_data.get("email", ""))
        self._email.setPlaceholderText(t("email"))
        form.addRow(t("email"), self._email)

        self._language = QComboBox()
        self._language.addItems(get_available_languages())
        lang = user_data.get("language", "Русский")
        idx = self._language.findText(lang)
        if idx >= 0:
            self._language.setCurrentIndex(idx)
        form.addRow(t("language"), self._language)

        self._autostart = QCheckBox(t("autostart_desc"))
        self._autostart.setChecked(user_data.get("autostart", False))
        form.addRow(t("autostart"), self._autostart)

        self._tray = QCheckBox(t("system_tray_desc"))
        self._tray.setChecked(user_data.get("minimize_to_tray", True))
        form.addRow(t("system_tray"), self._tray)

        layout.addLayout(form)

        btn_box = QHBoxLayout()
        cancel_btn = QPushButton(t("cancel"))
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)
        save_btn = QPushButton(t("save"))
        save_btn.clicked.connect(self.accept)
        btn_box.addWidget(save_btn)
        layout.addLayout(btn_box)

    def get_data(self) -> dict:
        return {
            "display_name": self._display_name.text().strip(),
            "email": self._email.text().strip(),
            "language": self._language.currentText(),
            "autostart": self._autostart.isChecked(),
            "minimize_to_tray": self._tray.isChecked(),
        }


class MainWindow(QWidget):
    def __init__(self, user_data: dict, spotify_client: SpotifyClient | None = None) -> None:
        super().__init__()
        self._user_data = user_data
        self._user_id = user_data.get("id", "")
        self._spotify = spotify_client
        self._player = MusicPlayer()
        self._current_track_data: dict | None = None
        self._tray: TrayIcon | None = None
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(400)
        self._search_timer.timeout.connect(self._perform_search)
        load_translations(user_data.get("language", "Русский"))
        self.setWindowTitle("SanGlow")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 800)
        self._setup_ui()
        self._player.track_changed.connect(self._on_track_changed)
        self._setup_tray()

    def _setup_tray(self) -> None:
        self._tray = TrayIcon(self._player, self)
        self._tray.show_clicked.connect(self._restore_from_tray)
        self._tray.quit_clicked.connect(self._force_quit)
        self._tray.play_pause_clicked.connect(self._toggle_play_from_tray)
        self._tray.next_clicked.connect(lambda: self._player.stop())
        self._tray.prev_clicked.connect(lambda: self._player.stop())
        self._tray.stop_clicked.connect(self._player.stop)
        self._tray.show()

    def _restore_from_tray(self) -> None:
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _force_quit(self) -> None:
        self._player.cleanup()
        if self._tray:
            self._tray.hide()
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().quit()

    def _toggle_play_from_tray(self) -> None:
        if self._player.is_playing:
            self._player.pause()
        elif self._player.is_paused:
            self._player.resume()

    def _open_profile_settings(self) -> None:
        dialog = ProfileDialog(self._user_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            old_lang = self._user_data.get("language", "Русский")
            self._user_data.update(data)
            new_lang = data.get("language", "Русский")
            if old_lang != new_lang:
                load_translations(new_lang)
            QMessageBox.information(self, "SanGlow", t("profile_saved"))

    def changeEvent(self, event) -> None:
        if event.type() == event.Type.WindowStateChange:
            if self.isMinimized():
                event.ignore()
                return
        super().changeEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showMaximized()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.showMaximized()
        else:
            super().keyPressEvent(event)

    def _setup_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.setSpacing(0)

        nav_area = QFrame()
        nav_area.setStyleSheet("background: #121212; border-radius: 8px; margin: 8px;")
        nav_layout = QVBoxLayout(nav_area)
        nav_layout.setContentsMargins(12, 16, 12, 8)
        nav_layout.setSpacing(4)

        logo = QLabel("  SanGlow")
        logo.setStyleSheet("font-size: 22px; font-weight: 800; color: #e8734a; padding: 4px 8px; background: transparent;")
        nav_layout.addWidget(logo)
        nav_layout.addSpacing(12)

        self._nav_buttons = []
        nav_items = [
            ("\U0001F3E0", t("home"), 0),
            ("\U0001F50D", t("search"), 1),
            ("\U0001F4DA", t("library"), 2),
            ("\u26A1", t("my_waves"), 3),
        ]
        for icon, label, idx in nav_items:
            btn = QPushButton(f"  {icon}    {label}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(42)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            nav_layout.addWidget(btn)
            self._nav_buttons.append(btn)
        self._nav_buttons[0].setChecked(True)
        nav_layout.addStretch()
        sb.addWidget(nav_area)

        lib_header = QFrame()
        lib_header.setStyleSheet("background: #121212; margin: 0 8px; border-radius: 8px;")
        lib_layout = QVBoxLayout(lib_header)
        lib_layout.setContentsMargins(16, 12, 16, 8)
        lib_label = QLabel(t("library"))
        lib_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #ffffff; background: transparent;")
        lib_layout.addWidget(lib_label)
        sb.addWidget(lib_header)

        playlist_scroll = QScrollArea()
        playlist_scroll.setWidgetResizable(True)
        playlist_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        playlist_scroll.setStyleSheet("background: #121212; border: none; margin: 0 8px;")
        self._playlist_list_widget = QWidget()
        self._playlist_list_layout = QVBoxLayout(self._playlist_list_widget)
        self._playlist_list_layout.setContentsMargins(8, 4, 8, 4)
        self._playlist_list_layout.setSpacing(2)
        self._playlist_list_layout.addStretch()
        playlist_scroll.setWidget(self._playlist_list_widget)
        sb.addWidget(playlist_scroll, stretch=1)

        profile_frame = QFrame()
        profile_frame.setStyleSheet("QFrame { background: #121212; border-radius: 8px; margin: 0 8px 8px 8px; } QFrame:hover { background: #1a1a1a; }")
        profile_frame.setFixedHeight(52)
        profile_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        profile_frame.mousePressEvent = lambda e: self._open_profile_settings()
        pl = QHBoxLayout(profile_frame)
        pl.setContentsMargins(12, 8, 12, 8)
        pl.setSpacing(10)
        avatar = QLabel(self._user_data.get("username", "U")[0].upper())
        avatar.setFixedSize(34, 34)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("background-color: #e8734a; color: #ffffff; border-radius: 17px; font-size: 14px; font-weight: 700;")
        pl.addWidget(avatar)
        name = QLabel(self._user_data.get("display_name", self._user_data.get("username", "")))
        name.setStyleSheet("font-size: 13px; font-weight: 600; color: #ffffff; background: transparent;")
        pl.addWidget(name)
        pl.addStretch()
        sb.addWidget(profile_frame)

        main_layout.addWidget(sidebar)

        content_area = QVBoxLayout()
        content_area.setContentsMargins(0, 0, 0, 0)
        content_area.setSpacing(0)

        self._content_stack = QStackedWidget()
        self._content_stack.addWidget(self._create_home_page())
        self._content_stack.addWidget(self._create_search_page())
        self._content_stack.addWidget(self._create_library_page())
        self._content_stack.addWidget(self._create_waves_page())
        content_area.addWidget(self._content_stack, stretch=1)

        self._player_bar = PlayerBar(self._player)
        content_area.addWidget(self._player_bar)

        content_widget = QWidget()
        content_widget.setLayout(content_area)
        main_layout.addWidget(content_widget, stretch=1)

    def _switch_page(self, idx: int) -> None:
        self._content_stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == idx)

    def _create_home_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: #121212;")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: #121212; border: none;")

        inner = QWidget()
        inner.setStyleSheet("background: #121212;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(24)

        greeting = get_greeting(self._user_data.get("display_name"))
        greeting_label = QLabel(f"{greeting.emoji}  {greeting.text}")
        greeting_label.setStyleSheet("font-size: 30px; font-weight: 800; color: #ffffff; padding: 0;")
        layout.addWidget(greeting_label)

        quick_grid = QGridLayout()
        quick_grid.setSpacing(12)
        quick_labels = [t("recently_played"), t("your_top_tracks"), t("liked_song"),
                        t("discover_weekly"), t("release_radar"), t("daily_mix")]
        quick_colors = ["#503750", "#1E3264", "#8D67AB", "#1E3264", "#E8115B", "#148A08"]
        for i, (lbl_text, color) in enumerate(zip(quick_labels, quick_colors)):
            card = QFrame()
            card.setFixedHeight(64)
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.setStyleSheet(f"QFrame {{ background: {color}; border-radius: 6px; }} QFrame:hover {{ background: {color}; opacity: 0.9; }}")
            cl = QHBoxLayout(card)
            cl.setContentsMargins(16, 0, 16, 0)
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #ffffff; background: transparent;")
            cl.addWidget(lbl)
            quick_grid.addWidget(card, i // 3, i % 3)
        layout.addLayout(quick_grid)

        playlists = get_suggested_playlists()
        if playlists:
            pl_header = QLabel(t("recommendations_for_you"))
            pl_header.setStyleSheet("font-size: 22px; font-weight: 700; color: #ffffff;")
            layout.addWidget(pl_header)

            pl_grid = QGridLayout()
            pl_grid.setSpacing(16)
            for i, pl in enumerate(playlists[:6]):
                card = PlaylistCard(pl)
                card.clicked.connect(self._on_playlist_card_clicked)
                pl_grid.addWidget(card, i // 3, i % 3)
            layout.addLayout(pl_grid)

        if self._spotify:
            section1 = QLabel(t("recently_played"))
            section1.setStyleSheet("font-size: 22px; font-weight: 700; color: #ffffff;")
            layout.addWidget(section1)
            self._recent_list = QListWidget()
            self._recent_list.setMaximumHeight(200)
            self._recent_list.setStyleSheet("background: transparent; border: none;")
            layout.addWidget(self._recent_list)

            section2 = QLabel(t("your_top_tracks"))
            section2.setStyleSheet("font-size: 22px; font-weight: 700; color: #ffffff;")
            layout.addWidget(section2)
            self._top_tracks_list = QListWidget()
            self._top_tracks_list.setMaximumHeight(200)
            self._top_tracks_list.setStyleSheet("background: transparent; border: none;")
            layout.addWidget(self._top_tracks_list)

        layout.addStretch()
        scroll.setWidget(inner)

        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        return page

    def _on_playlist_card_clicked(self, playlist: dict) -> None:
        QMessageBox.information(self, playlist.get("name", "Playlist"), playlist.get("description", ""))

    def _create_search_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: #121212;")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: #121212; border: none;")

        inner = QWidget()
        inner.setStyleSheet("background: #121212;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(24)

        self._search_bar = QLineEdit()
        self._search_bar.setPlaceholderText(t("search_placeholder"))
        self._search_bar.setFixedHeight(48)
        self._search_bar.setStyleSheet("""
            QLineEdit {
                background: #2a2a2a; color: #ffffff; border: 2px solid transparent;
                border-radius: 24px; padding: 0 20px; font-size: 15px;
            }
            QLineEdit:focus { border-color: #ffffff; background: #333333; }
            QLineEdit::placeholder { color: #727272; }
        """)
        self._search_bar.textChanged.connect(self._on_search_text_changed)
        self._search_bar.returnPressed.connect(self._perform_search)
        layout.addWidget(self._search_bar)

        self._search_categories_widget = QWidget()
        self._search_categories_widget.setStyleSheet("background: transparent;")
        cat_grid = QGridLayout(self._search_categories_widget)
        cat_grid.setSpacing(16)
        cat_grid.setContentsMargins(0, 0, 0, 0)
        for i, cat in enumerate(_SEARCH_CATEGORIES):
            card = CategoryCard(cat)
            card.clicked.connect(self._on_category_clicked)
            cat_grid.addWidget(card, i // 4, i % 4)
        layout.addWidget(self._search_categories_widget)

        self._search_results_container = QWidget()
        self._search_results_container.setStyleSheet("background: transparent;")
        self._search_results_layout = QVBoxLayout(self._search_results_container)
        self._search_results_layout.setContentsMargins(0, 0, 0, 0)
        self._search_results_layout.setSpacing(8)
        self._search_results_layout.addStretch()
        layout.addWidget(self._search_results_container)

        layout.addStretch()
        scroll.setWidget(inner)

        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        return page

    def _on_search_text_changed(self, text: str) -> None:
        if text.strip():
            self._search_categories_widget.hide()
            self._search_timer.start()
        else:
            self._search_categories_widget.show()
            self._clear_search_results()

    def _on_category_clicked(self, cat: dict) -> None:
        QMessageBox.information(self, cat["name"], f"Browse {cat['name']}")

    def _clear_search_results(self) -> None:
        while self._search_results_layout.count():
            item = self._search_results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _create_library_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: #121212;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel(t("library"))
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #ffffff;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #121212; }
            QTabBar::tab { background: transparent; color: #b3b3b3; padding: 10px 24px;
                           border: none; font-size: 14px; font-weight: 600; border-bottom: 3px solid transparent; }
            QTabBar::tab:selected { color: #ffffff; border-bottom-color: #ffffff; }
            QTabBar::tab:hover { color: #ffffff; }
        """)
        self._playlists_list = QListWidget()
        self._playlists_list.setStyleSheet("background: transparent; border: none; font-size: 14px;")
        tabs.addTab(self._playlists_list, t("library"))
        self._favorites_list = QListWidget()
        self._favorites_list.setStyleSheet("background: transparent; border: none; font-size: 14px;")
        tabs.addTab(self._favorites_list, t("liked_song"))
        layout.addWidget(tabs)
        return page

    def _create_waves_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: #121212;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        top = QHBoxLayout()
        title = QLabel(t("my_waves"))
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #ffffff;")
        top.addWidget(title)
        top.addStretch()
        create_btn = QPushButton(f"+ {t('create_wave')}")
        create_btn.setObjectName("primaryButton")
        create_btn.setFixedHeight(40)
        create_btn.clicked.connect(self._create_wave)
        top.addWidget(create_btn)
        layout.addLayout(top)

        self._waves_list = QListWidget()
        self._waves_list.currentRowChanged.connect(self._on_wave_selected)
        self._waves_list.setStyleSheet("background: transparent; border: none; font-size: 14px;")
        layout.addWidget(self._waves_list)

        self._wave_tracks_list = QListWidget()
        self._wave_tracks_list.setStyleSheet("background: transparent; border: none; font-size: 14px;")
        layout.addWidget(self._wave_tracks_list)
        return page

    def _perform_search(self) -> None:
        query = self._search_bar.text().strip() if hasattr(self, '_search_bar') else ""
        if not query or not self._spotify:
            return
        try:
            results = self._spotify.search(query, search_type="track")
            self._clear_search_results()
            for track in results.get("tracks", []):
                row = TrackRow(track, self._search_results_layout.count(), self._user_id)
                row.clicked.connect(self._on_track_row_clicked)
                self._search_results_layout.addWidget(row)
        except Exception:
            pass

    def _on_track_row_clicked(self, data: dict) -> None:
        self._current_track_data = data
        self._player.load_and_play(data)

    def _on_track_changed(self, track: dict) -> None:
        self._current_track_data = track

    def _create_wave(self) -> None:
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, t("create_wave"), t("wave_name"))
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
                    tracks = svc.get_wave_tracks(wave_id, self._user_id)
                self._wave_tracks_list.clear()
                for t in tracks:
                    self._wave_tracks_list.addItem(f"{t['name']} \u2014 {t['artist']}")

    def _load_waves(self) -> None:
        with get_db_session() as db:
            svc = SocialService(db)
            waves = svc.get_waves(self._user_id)
        self._waves_list.clear()
        for w in waves:
            item = QListWidgetItem(f"\u26A1  {w['name']}  ({w['track_count']})")
            item.setData(Qt.ItemDataRole.UserRole, w["id"])
            self._waves_list.addItem(item)

    def load_data(self) -> None:
        if not self._spotify:
            return
        try:
            for track in self._spotify.get_recently_played(limit=10):
                self._recent_list.addItem(f"{track.name} \u2014 {track.artist}")
            for track in self._spotify.get_top_tracks(limit=10):
                self._top_tracks_list.addItem(f"{track.name} \u2014 {track.artist}")
            for pl in self._spotify.get_user_playlists(limit=50):
                self._playlists_list.addItem(f"{pl.name}  ({pl.track_count})")
        except Exception:
            pass
        self._load_waves()

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()
        if self._tray:
            self._tray.show()
            self._tray._tray.showMessage(
                "SanGlow",
                "SanGlow is minimized to tray. Double-click to restore.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
