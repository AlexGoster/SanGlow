from __future__ import annotations

import logging
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont, QIcon

from src.models.database import init_db
from src.ui.styles.dark_theme import SANGLOW_DARK
from src.ui.widgets.login_dialog import LoginDialog
from src.ui.main_window import MainWindow
from src.spotify.auth import SpotifyAuth
from src.spotify.client import SpotifyClient

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )

    try:
        init_db()
    except Exception as e:
        logger.critical("Database initialization failed: %s", e)
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
    spotify_client: SpotifyClient | None = None

    def on_login_success(user_data: dict) -> None:
        nonlocal spotify_client
        try:
            spotify_client = SpotifyClient(SpotifyAuth().get_cached_token())
        except Exception:
            pass
        window = MainWindow(user_data, spotify_client)
        if icon_path.exists():
            window.setWindowIcon(QIcon(str(icon_path)))
        window.show()
        if spotify_client:
            window.load_data()

    login.login_successful.connect(on_login_success)

    if login.exec() != 1:
        sys.exit(0)

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical("Fatal error: %s", e, exc_info=True)
        sys.exit(1)
