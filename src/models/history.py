from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ListeningHistory(Base):
    __tablename__ = "listening_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    spotify_track_id: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(255))
    artist: Mapped[str] = mapped_column(String(255))
    album: Mapped[str | None] = mapped_column(String(255), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    listened_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    listen_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user = relationship("User", back_populates="history")
