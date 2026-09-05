from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFileDialog, QListWidget, QListWidgetItem,
    QMessageBox, QTabWidget, QWidget, QFrame, QProgressBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from src.i18n import t


class ImportWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, int)

    def __init__(self, source: str, query: str = "", url: str = "", folder: str = "") -> None:
        super().__init__()
        self._source = source
        self._query = query
        self._url = url
        self._folder = folder

    def run(self) -> None:
        try:
            if self._source == "local_folder":
                self._import_local_folder()
            elif self._source == "spotify_url":
                self._import_spotify_url()
            elif self._source == "yandex_url":
                self._import_yandex_url()
            elif self._source == "youtube_url":
                self._import_youtube_url()
            elif self._source == "soundcloud_url":
                self._import_soundcloud_url()
            elif self._source == "zvuk_url":
                self._import_zvuk_url()
            elif self._source == "telegram_url":
                self._import_telegram_url()
        except Exception as e:
            self.error.emit(str(e))

    def _import_local_folder(self) -> None:
        from src.importers.local_music import LocalMusicLibrary
        lib = LocalMusicLibrary()
        count = lib.add_folder(self._folder)
        self.finished.emit([{"name": t("local_folder_imported"), "artist": f"{count} {t('tracks_found')}"}])

    def _import_spotify_url(self) -> None:
        from src.spotify.client import SpotifyClient
        from src.spotify.auth import SpotifyAuth
        try:
            client = SpotifyClient(SpotifyAuth().get_cached_token())
            playlist_id = self._url.split("playlist/")[-1].split("?")[0]
            tracks = client.get_playlist_tracks(playlist_id)
            self.finished.emit([{"name": t.name, "artist": t.artist, "preview_url": t.preview_url} for t in tracks])
        except Exception as e:
            self.error.emit(f"Spotify: {e}")

    def _import_yandex_url(self) -> None:
        from src.importers.yandex_music import YandexMusicImporter
        importer = YandexMusicImporter()
        try:
            tracks = importer.import_from_url(self._url)
            self.finished.emit([{"name": t.title, "artist": t.artist} for t in tracks])
        finally:
            importer.close()

    def _import_youtube_url(self) -> None:
        from src.importers.youtube_music import YouTubeMusicImporter
        importer = YouTubeMusicImporter()
        try:
            tracks = importer.import_from_url(self._url)
            self.finished.emit([{"name": t.title, "artist": t.artist} for t in tracks])
        finally:
            importer.close()

    def _import_soundcloud_url(self) -> None:
        from src.importers.soundcloud import SoundCloudImporter
        importer = SoundCloudImporter()
        try:
            tracks = importer.import_from_url(self._url)
            self.finished.emit([{"name": t.title, "artist": t.artist} for t in tracks])
        finally:
            importer.close()

    def _import_zvuk_url(self) -> None:
        from src.importers.zvuk_music import ZvukMusicImporter
        importer = ZvukMusicImporter()
        try:
            tracks = importer.import_from_url(self._url)
            self.finished.emit([{"name": t.title, "artist": t.artist} for t in tracks])
        except Exception as e:
            self.error.emit(f"Zvuk: {e}")

    def _import_telegram_url(self) -> None:
        from src.importers.telegram_music import TelegramMusicImporter
        importer = TelegramMusicImporter()
        try:
            tracks = importer.import_from_url(self._url)
            self.finished.emit([{"name": t.title, "artist": t.artist} for t in tracks])
        finally:
            importer.close()


class ImportDialog(QDialog):
    import_completed = pyqtSignal(list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"SanGlow — {t('import_music')}")
        self.setMinimumSize(600, 500)
        self.setStyleSheet("""
            QDialog { background: #1e1e1e; color: #e0d6cc; }
            QLabel { color: #e0d6cc; font-size: 13px; }
            QLineEdit { background: #252525; color: #e0d6cc; border: 1px solid #3a3a3a;
                         border-radius: 6px; padding: 8px 12px; font-size: 13px; }
            QLineEdit:focus { border-color: #e8734a; }
            QComboBox { background: #252525; color: #e0d6cc; border: 1px solid #3a3a3a;
                         border-radius: 6px; padding: 8px 12px; font-size: 13px; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background: #252525; color: #e0d6cc; selection-background-color: #e8734a; }
            QListWidget { background: #252525; color: #e0d6cc; border: 1px solid #3a3a3a;
                          border-radius: 6px; font-size: 13px; }
            QListWidget::item { padding: 8px; }
            QListWidget::item:selected { background: #e8734a; color: #ffffff; }
            QPushButton { background: #e8734a; color: #ffffff; border: none; border-radius: 6px;
                          padding: 8px 20px; font-size: 13px; font-weight: 600; }
            QPushButton:hover { background: #f28150; }
            QPushButton#browseBtn { background: #3a3a3a; color: #e0d6cc; }
            QPushButton#browseBtn:hover { background: #4a4a4a; }
            QPushButton#cancelBtn { background: #3a3a3a; color: #e0d6cc; }
            QPushButton#cancelBtn:hover { background: #4a4a4a; }
            QProgressBar { border: 1px solid #3a3a3a; border-radius: 4px; text-align: center; color: #ffffff; }
            QProgressBar::chunk { background: #e8734a; border-radius: 3px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel(t("import_music"))
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #e8734a; margin-bottom: 8px;")
        layout.addWidget(title)

        source_label = QLabel(t("import_source"))
        layout.addWidget(source_label)

        self._source_combo = QComboBox()
        self._source_combo.addItems([
            t("local_folder"),
            t("spotify_url"),
            t("yandex_url"),
            t("youtube_url"),
            t("soundcloud_url"),
            t("zvuk_url"),
            t("telegram_url"),
        ])
        self._source_combo.currentIndexChanged.connect(self._on_source_changed)
        layout.addWidget(self._source_combo)

        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText(t("enter_url_or_playlist"))
        layout.addWidget(self._url_input)

        folder_row = QHBoxLayout()
        self._folder_input = QLineEdit()
        self._folder_input.setPlaceholderText(t("select_folder"))
        self._folder_input.setReadOnly(True)
        folder_row.addWidget(self._folder_input)

        self._browse_btn = QPushButton(t("browse"))
        self._browse_btn.setObjectName("browseBtn")
        self._browse_btn.clicked.connect(self._browse_folder)
        folder_row.addWidget(self._browse_btn)
        layout.addLayout(folder_row)

        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._results_list = QListWidget()
        layout.addWidget(self._results_list, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._cancel_btn = QPushButton(t("cancel"))
        self._cancel_btn.setObjectName("cancelBtn")
        self._cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self._cancel_btn)

        self._import_btn = QPushButton(t("import"))
        self._import_btn.clicked.connect(self._start_import)
        btn_row.addWidget(self._import_btn)

        layout.addLayout(btn_row)

        self._worker: ImportWorker | None = None

    def _on_source_changed(self, index: int) -> None:
        is_local = index == 0
        self._url_input.setVisible(not is_local)
        self._folder_input.setVisible(is_local)
        self._browse_btn.setVisible(is_local)

    def _browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, t("select_folder"))
        if folder:
            self._folder_input.setText(folder)

    def _start_import(self) -> None:
        source_index = self._source_combo.currentIndex()
        source_keys = ["local_folder", "spotify_url", "yandex_url", "youtube_url", "soundcloud_url", "zvuk_url", "telegram_url"]
        source = source_keys[source_index]

        url = self._url_input.text().strip() if source_index != 0 else ""
        folder = self._folder_input.text().strip() if source_index == 0 else ""

        if source == "local_folder" and not folder:
            QMessageBox.warning(self, t("error"), t("select_folder"))
            return
        if source != "local_folder" and not url:
            QMessageBox.warning(self, t("error"), t("enter_url_or_playlist"))
            return

        self._progress.setVisible(True)
        self._progress.setRange(0, 0)
        self._import_btn.setEnabled(False)
        self._results_list.clear()

        self._worker = ImportWorker(source, url=url, folder=folder)
        self._worker.finished.connect(self._on_import_finished)
        self._worker.error.connect(self._on_import_error)
        self._worker.start()

    def _on_import_finished(self, tracks: list) -> None:
        self._progress.setVisible(False)
        self._import_btn.setEnabled(True)
        for track in tracks:
            name = track.get("name", "Unknown")
            artist = track.get("artist", "")
            item = QListWidgetItem(f"{name} — {artist}")
            self._results_list.addItem(item)
        if tracks:
            self.import_completed.emit(tracks)
        QMessageBox.information(self, t("success"), f"{t('imported')}: {len(tracks)} {t('tracks')}")

    def _on_import_error(self, error: str) -> None:
        self._progress.setVisible(False)
        self._import_btn.setEnabled(True)
        QMessageBox.critical(self, t("error"), error)
