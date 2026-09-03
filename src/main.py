from __future__ import annotations

import logging
import sys
import traceback
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont, QIcon

from src.models.database import init_db
from src.ui.styles.dark_theme import SANGLOW_DARK
from src.ui.widgets.login_dialog import LoginDialog
from src.ui.main_window import MainWindow
from src.spotify.auth import SpotifyAuth
from src.spotify.client import SpotifyClient
from src.utils.autostart import is_autostart_enabled, enable_autostart, disable_autostart

logger = logging.getLogger(__name__)


def _setup_logging() -> None:
    if getattr(sys, "frozen", False):
        from config.settings import USER_DATA_DIR
        log_dir = USER_DATA_DIR / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "sanglow.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[logging.StreamHandler(), file_handler],
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[logging.StreamHandler()],
        )


def main() -> None:
    _setup_logging()
    logger.info("SanGlow starting...")

    start_minimized = "--minimized" in sys.argv

    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.critical("Database initialization failed: %s", e, exc_info=True)
        _show_fatal_error(f"Database initialization failed:\n{e}")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("SanGlow")

    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).resolve().parent.parent

    icon_path = base / "assets" / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(SANGLOW_DARK)

    login = LoginDialog()
    main_window = None

    def on_login_success(user_data: dict) -> None:
        nonlocal main_window
        try:
            from src.spotify.client import SpotifyClient
            from src.spotify.auth import SpotifyAuth
            spotify_client = SpotifyClient(SpotifyAuth().get_cached_token())
        except Exception:
            spotify_client = None
        main_window = MainWindow(user_data, spotify_client)
        if icon_path.exists():
            main_window.setWindowIcon(QIcon(str(icon_path)))

        from src.utils.smtc import get_media_hotkeys
        hotkeys = get_media_hotkeys()
        hotkeys.register(
            play_pause=main_window._toggle_play_from_tray,
            next_track=lambda: main_window._player.stop(),
            prev_track=lambda: main_window._player.stop(),
            stop=main_window._player.stop,
        )

        if start_minimized:
            main_window.showMinimized()
        else:
            main_window.showMaximized()

        if spotify_client:
            main_window.load_data()

    login.login_successful.connect(on_login_success)

    if login.exec() != 1:
        sys.exit(0)

    sys.exit(app.exec())


def _show_fatal_error(msg: str) -> None:
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        QMessageBox.critical(None, "SanGlow - Fatal Error", msg)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical("Fatal error: %s", e, exc_info=True)
        _show_fatal_error(f"Fatal error:\n{e}\n\nSee logs for details.")
        sys.exit(1)
