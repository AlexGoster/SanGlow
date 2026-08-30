from __future__ import annotations

import logging
import os
import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs

from spotipy.oauth2 import SpotifyOAuth

from config.settings import get_spotify_config

logger = logging.getLogger(__name__)


class _CallbackHandler(BaseHTTPRequestHandler):
    auth_code: str | None = None
    state_param: str | None = None

    def do_GET(self) -> None:
        if "/callback" in self.path:
            query = parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
            returned_state = query.get("state", [None])[0]
            if _CallbackHandler.state_param and returned_state != _CallbackHandler.state_param:
                self.send_response(403)
                self.end_headers()
                return
            _CallbackHandler.auth_code = query.get("code", [None])[0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Auth OK! Close this.</h1>")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass


class SpotifyAuth:
    def __init__(self) -> None:
        config = get_spotify_config()
        cache_dir = Path.home() / ".config" / "sanglow"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = str(cache_dir / ".spotify_cache")
        try:
            os.chmod(cache_path, 0o600)
        except (OSError, PermissionError):
            pass
        self._auth_manager = SpotifyOAuth(
            client_id=config.client_id,
            client_secret=config.client_secret.get_secret_value(),
            redirect_uri=config.redirect_uri,
            scope=config.scope,
            cache_path=cache_path,
        )

    def get_auth_url(self) -> str:
        state = secrets.token_urlsafe(32)
        _CallbackHandler.state_param = state
        return self._auth_manager.get_authorize_url() + f"&state={state}"

    def authenticate_with_browser(self) -> str | None:
        webbrowser.open(self.get_auth_url())
        server = HTTPServer(("127.0.0.1", 0), _CallbackHandler)
        server.timeout = 60
        _CallbackHandler.auth_code = None
        while _CallbackHandler.auth_code is None:
            server.handle_request()
        server.server_close()
        return _CallbackHandler.auth_code

    def get_cached_token(self) -> str | None:
        token_info = self._auth_manager.get_cached_token()
        return token_info.get("access_token") if token_info else None

    def refresh_if_needed(self) -> str | None:
        token_info = self._auth_manager.get_cached_token()
        if token_info and self._auth_manager.is_token_expired(token_info):
            token_info = self._auth_manager.refresh_access_token(token_info["refresh_token"])
        return token_info.get("access_token") if token_info else None
