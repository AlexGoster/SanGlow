from __future__ import annotations

import uuid
from datetime import datetime, timezone

import bcrypt
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    spotify_user_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    spotify_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    spotify_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_login_attempts: Mapped[int] = mapped_column(default=0)
    last_failed_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    password_changed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    _old_passwords: Mapped[str | None] = mapped_column("old_passwords", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    playlists = relationship("Playlist", back_populates="user", lazy="selectin")
    history = relationship("ListeningHistory", back_populates="user", lazy="selectin")

    def set_password(self, password: str) -> None:
        from config.settings import get_security_config
        from src.utils.encryption import EncryptionManager
        rounds = get_security_config().bcrypt_rounds
        if self.password_hash:
            try:
                enc = EncryptionManager()
                old_data = enc.decrypt_dict(self._old_passwords or "")
                hashes = old_data.get("hashes", [])
                hashes.append(self.password_hash)
                if len(hashes) > 10:
                    hashes = hashes[-10:]
                self._old_passwords = enc.encrypt_dict({"hashes": hashes})
            except Exception:
                pass
        salt = bcrypt.gensalt(rounds=rounds)
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        self.password_changed_at = datetime.now(timezone.utc)

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def set_spotify_tokens(self, access_token: str | None, refresh_token: str | None) -> None:
        from src.utils.encryption import EncryptionManager
        enc = EncryptionManager()
        self.spotify_access_token = enc.encrypt(access_token) if access_token else None
        self.spotify_refresh_token = enc.encrypt(refresh_token) if refresh_token else None

    def get_spotify_tokens(self) -> tuple[str | None, str | None]:
        from src.utils.encryption import EncryptionManager
        enc = EncryptionManager()
        access = enc.decrypt(self.spotify_access_token) if self.spotify_access_token else None
        refresh = enc.decrypt(self.spotify_refresh_token) if self.spotify_refresh_token else None
        return access, refresh

    def was_password_used(self, password: str, max_history: int = 5) -> bool:
        from src.utils.encryption import EncryptionManager
        try:
            enc = EncryptionManager()
            old_data = enc.decrypt_dict(self._old_passwords or "")
            hashes = old_data.get("hashes", [])
            for h in hashes[-max_history:]:
                if bcrypt.checkpw(password.encode("utf-8"), h.encode("utf-8")):
                    return True
        except Exception:
            pass
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat(),
        }

    def to_safe_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
        }
