from __future__ import annotations

import uuid
from datetime import datetime

import bcrypt
from sqlalchemy import Boolean, DateTime, String, Text
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    playlists = relationship("Playlist", back_populates="user", lazy="selectin")
    history = relationship("ListeningHistory", back_populates="user", lazy="selectin")

    def set_password(self, password: str) -> None:
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def to_dict(self) -> dict:
        return {
            "id": self.id, "username": self.username, "email": self.email,
            "display_name": self.display_name, "avatar_url": self.avatar_url,
            "bio": self.bio, "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }
