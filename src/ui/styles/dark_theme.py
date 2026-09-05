from __future__ import annotations

from pathlib import Path


_STYLES_DIR = Path(__file__).parent


def load_theme() -> str:
    qss_file = _STYLES_DIR / "theme.qss"
    if qss_file.exists():
        return qss_file.read_text(encoding="utf-8")
    return ""


SANGLOW_DARK = load_theme()
