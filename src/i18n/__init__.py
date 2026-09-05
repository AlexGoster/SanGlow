from __future__ import annotations

import json
from pathlib import Path

_translations: dict[str, str] = {}
_current_lang: str = "Русский"

_LANG_DIR = Path(__file__).parent


def load_translations(lang: str) -> None:
    global _translations, _current_lang
    _current_lang = lang
    lang_file = _LANG_DIR / f"{lang}.json"
    if lang_file.exists():
        with open(lang_file, encoding="utf-8") as f:
            _translations = json.load(f)
    else:
        _translations = {}


def t(key: str, **kwargs) -> str:
    text = _translations.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def get_current_lang() -> str:
    return _current_lang


def get_available_languages() -> list[str]:
    return ["Русский", "English", "Deutsch", "Français", "Español"]
