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
    return bool(re.match(r"^https?://[a-zA-Z0-9._%+-]+\\.[a-zA-Z]{2,}", url))
