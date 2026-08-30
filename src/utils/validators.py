from __future__ import annotations

import html
import re


def sanitize_input(text: str, max_length: int = 1000) -> str:
    text = html.escape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()[:max_length]


def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[<>:"/\\|?*]', "", filename).strip(". ")
    return (filename or "unnamed")[:255]


def validate_url(url: str) -> bool:
    if len(url) > 2048:
        return False
    return bool(re.match(r"^https?://[a-zA-Z0-9._%+-]+\.[a-zA-Z]{2,}(/.*)?$", url))


def sanitize_display_name(name: str) -> str:
    name = re.sub(r"[{}\[\]()`^]", "", name)
    return name.strip()[:100] or "User"


def sanitize_track_id(track_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "", track_id)[:200] or "unknown"


def validate_source(source: str) -> str:
    allowed = ("local", "spotify", "youtube", "yandex", "soundcloud", "telegram", "zvuk")
    return source if source in allowed else "local"
