from __future__ import annotations

import sys
from pathlib import Path
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"


class SpotifyConfig(BaseSettings):
    client_id: str = Field(default="", alias="SPOTIFY_CLIENT_ID")
    client_secret: SecretStr = Field(default=SecretStr(""), alias="SPOTIFY_CLIENT_SECRET")
    redirect_uri: str = Field(
        default="http://localhost:8888/callback", alias="SPOTIFY_REDIRECT_URI"
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


class SecurityConfig(BaseSettings):
    jwt_secret_key: SecretStr = Field(default=SecretStr("sanglow-dev-secret-key-change-in-production"), alias="JWT_SECRET_KEY")
    encryption_key: SecretStr = Field(default=SecretStr("sanglow-dev-encryption-key-change-in-production"), alias="ENCRYPTION_KEY")
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 60 * 24
    bcrypt_rounds: int = 12

    model_config = {"env_prefix": "", "extra": "ignore"}


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
        db_path = Path(sys.executable).parent / "sanglow.db"
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
