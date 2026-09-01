from __future__ import annotations

import html
import ipaddress
import re
from urllib.parse import urlparse

import socket


def sanitize_input(text: str, max_length: int = 1000) -> str:
    text = html.escape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()[:max_length]


def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[<>:"/\\|?*]', "", filename).strip(". ")
    filename = re.sub(r"\.\.", "", filename)
    return (filename or "unnamed")[:255]


_BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def _is_private_ip(hostname: str) -> bool:
    try:
        ip = ipaddress.ip_address(hostname)
        return any(ip in net for net in _BLOCKED_NETWORKS)
    except ValueError:
        pass
    try:
        resolved = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC)
        for family, _, _, _, sockaddr in resolved:
            ip = ipaddress.ip_address(sockaddr[0])
            if any(ip in net for net in _BLOCKED_NETWORKS):
                return True
    except (socket.gaierror, ValueError):
        pass
    return False


def validate_url(url: str) -> bool:
    if len(url) > 2048:
        return False
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in ("https",):
        return False
    if not parsed.hostname:
        return False
    if _is_private_ip(parsed.hostname):
        return False
    blocked_hosts = ("localhost", "127.0.0.1", "0.0.0.0", "::1", "[::1]")
    if parsed.hostname.lower() in blocked_hosts:
        return False
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+\.[a-zA-Z]{2,}$", parsed.hostname))


def sanitize_display_name(name: str) -> str:
    name = re.sub(r"[{}\[\]()`^<>\"'/\\&]", "", name)
    return name.strip()[:100] or "User"


def sanitize_track_id(track_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "", track_id)[:200] or "unknown"


def validate_source(source: str) -> str:
    allowed = ("local", "spotify", "youtube", "yandex", "soundcloud", "telegram", "zvuk")
    return source if source in allowed else "local"
