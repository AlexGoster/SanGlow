from __future__ import annotations

import logging
import os
import secrets
import sys
from pathlib import Path
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
    USER_DATA_DIR = Path(os.environ.get("APPDATA", Path.home() / ".config")) / "SanGlow"
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    USER_DATA_DIR = BASE_DIR

DATA_DIR = USER_DATA_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"


class SpotifyConfig(BaseSettings):
    client_id: str = Field(default="", alias="SPOTIFY_CLIENT_ID")
    client_secret: SecretStr = Field(default=SecretStr(""), alias="SPOTIFY_CLIENT_SECRET")
    redirect_uri: str = Field(
        default="http://127.0.0.1:0/callback", alias="SPOTIFY_REDIRECT_URI"
    )
    scope: str = (
        "user-read-private user-read-email user-library-read "
        "user-library-modify user-read-recently-played user-top-read "
        "playlist-read-private playlist-modify-public playlist-modify-private "
        "user-read-playback-state user-modify-playback-state user-read-currently-playing"
    )

    model_config = {"env_prefix": "", "extra": "ignore"}


class ZvukConfig(BaseSettings):
    token: str = Field(default="", alias="ZVUK_TOKEN")

    model_config = {"env_prefix": "", "extra": "ignore"}


def _generate_or_validate_key(env_var: str, label: str) -> str:
    val = os.environ.get(env_var, "")
    if not val or "change-in-production" in val:
        key_file = DATA_DIR / f"{env_var.lower()}.key"
        if key_file.exists():
            val = key_file.read_text().strip()
            if len(val) < 32:
                logger.warning("Key too short, regenerating: %s", label)
                val = ""
        if not val:
            val = secrets.token_urlsafe(64)
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            key_file.write_text(val)
            try:
                os.chmod(key_file, 0o600)
            except (OSError, PermissionError):
                pass
    if len(val) < 32:
        raise ValueError(f"Key for {label} is too short (min 32 chars)")
    return val


class SecurityConfig(BaseSettings):
    jwt_secret_key: SecretStr = Field(default=SecretStr(""), alias="JWT_SECRET_KEY")
    encryption_key: SecretStr = Field(default=SecretStr(""), alias="ENCRYPTION_KEY")
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 15
    refresh_expire_days: int = 7
    bcrypt_rounds: int = 14
    max_login_attempts: int = 5
    lockout_minutes: int = 15
    max_password_length: int = 128
    session_timeout_minutes: int = 30

    model_config = {"env_prefix": "", "extra": "ignore"}

    def model_post_init(self, __context: object) -> None:
        if not self.jwt_secret_key.get_secret_value():
            self.jwt_secret_key = SecretStr(_generate_or_validate_key("JWT_SECRET_KEY", "JWT"))
        if not self.encryption_key.get_secret_value():
            self.encryption_key = SecretStr(_generate_or_validate_key("ENCRYPTION_KEY", "encryption"))


class DatabaseConfig(BaseSettings):
    url: str = Field(default="", alias="DATABASE_URL")
    echo: bool = False

    model_config = {"env_prefix": "", "extra": "ignore"}


class AppConfig(BaseSettings):
    name: str = Field(default="SanGlow", alias="APP_NAME")
    version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")

    model_config = {"env_prefix": "", "extra": "ignore"}


def _get_db_url() -> str:
    if getattr(sys, "frozen", False):
        db_path = USER_DATA_DIR / "sanglow.db"
    else:
        db_path = Path(__file__).resolve().parent.parent / "sanglow.db"
    return f"sqlite:///{db_path}"


@lru_cache
def get_spotify_config() -> SpotifyConfig:
    return SpotifyConfig()


@lru_cache
def get_zvuk_config() -> ZvukConfig:
    return ZvukConfig()


@lru_cache
def get_security_config() -> SecurityConfig:
    return SecurityConfig()


@lru_cache
def get_database_config() -> DatabaseConfig:
    cfg = DatabaseConfig()
    if not cfg.url:
        cfg.url = _get_db_url()
    return cfg


@lru_cache
def get_app_config() -> AppConfig:
    return AppConfig()
