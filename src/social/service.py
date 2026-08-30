from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from src.models.social import Comment, Like, Favorite, Wave, WaveTrack
from src.utils.validators import sanitize_input, sanitize_track_id, validate_source

logger = logging.getLogger(__name__)

_MAX_COMMENT_LEN = 2000
_MAX_NAME_LEN = 100
_MAX_FIELD_LEN = 500


def _sanitize(text: str, max_len: int = _MAX_COMMENT_LEN) -> str:
    text = sanitize_input(text, max_len)
    return text


def _sanitize_name(text: str, max_len: int = _MAX_NAME_LEN) -> str:
    text = re.sub(r"[<>&\"']", "", text.strip())
    return text[:max_len]


@dataclass
class SocialService:
    db: Session

    def add_comment(self, user_id: str, track_id: str, text: str, source: str = "local") -> Comment:
        text = _sanitize(text, _MAX_COMMENT_LEN)
        if not text:
            raise ValueError("Comment cannot be empty")
        source = validate_source(source)
        track_id = sanitize_track_id(track_id)
        comment = Comment(user_id=user_id, track_id=track_id, text=text, source=source)
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_comments(self, track_id: str, limit: int = 50) -> list[dict]:
        track_id = sanitize_track_id(track_id)
        comments = (
            self.db.query(Comment)
            .filter(Comment.track_id == track_id)
            .order_by(Comment.created_at.desc())
            .limit(min(limit, 100))
            .all()
        )
        return [c.to_dict() for c in comments]

    def delete_comment(self, comment_id: str, user_id: str) -> bool:
        c = self.db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == user_id).first()
        if c:
            self.db.delete(c)
            self.db.commit()
            return True
        return False

    def toggle_like(self, user_id: str, track_id: str, source: str = "local") -> bool:
        source = validate_source(source)
        track_id = sanitize_track_id(track_id)
        existing = self.db.query(Like).filter(Like.user_id == user_id, Like.track_id == track_id).first()
        if existing:
            self.db.delete(existing)
            self.db.commit()
            return False
        like = Like(user_id=user_id, track_id=track_id, source=source)
        self.db.add(like)
        self.db.commit()
        return True

    def is_liked(self, user_id: str, track_id: str) -> bool:
        track_id = sanitize_track_id(track_id)
        return self.db.query(Like).filter(Like.user_id == user_id, Like.track_id == track_id).first() is not None

    def get_like_count(self, track_id: str) -> int:
        track_id = sanitize_track_id(track_id)
        return self.db.query(Like).filter(Like.track_id == track_id).count()

    def add_favorite(self, user_id: str, track_data: dict) -> Favorite | None:
        track_id = sanitize_track_id(str(track_data.get("id", "")))
        existing = self.db.query(Favorite).filter(
            Favorite.user_id == user_id, Favorite.track_id == track_id
        ).first()
        if existing:
            return None
        fav = Favorite(
            user_id=user_id, track_id=track_id,
            source=validate_source(str(track_data.get("source", "local"))),
            title=_sanitize(str(track_data.get("name", track_data.get("title", "Unknown"))), _MAX_FIELD_LEN),
            artist=_sanitize(str(track_data.get("artist", "Unknown")), _MAX_FIELD_LEN),
            album=_sanitize(str(track_data.get("album") or ""), _MAX_FIELD_LEN),
            cover_url=track_data.get("cover_url"),
            preview_url=track_data.get("preview_url"),
            duration_ms=track_data.get("duration_ms"),
        )
        self.db.add(fav)
        self.db.commit()
        self.db.refresh(fav)
        return fav

    def remove_favorite(self, user_id: str, track_id: str) -> bool:
        track_id = sanitize_track_id(track_id)
        fav = self.db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.track_id == track_id).first()
        if fav:
            self.db.delete(fav)
            self.db.commit()
            return True
        return False

    def is_favorite(self, user_id: str, track_id: str) -> bool:
        track_id = sanitize_track_id(track_id)
        return self.db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.track_id == track_id).first() is not None

    def get_favorites(self, user_id: str, limit: int = 100) -> list[dict]:
        favs = (
            self.db.query(Favorite)
            .filter(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .limit(min(limit, 500))
            .all()
        )
        return [{"id": f.track_id, "name": f.title, "artist": f.artist, "album": f.album,
                 "cover_url": f.cover_url, "preview_url": f.preview_url,
                 "duration_ms": f.duration_ms, "source": f.source} for f in favs]

    def create_wave(self, user_id: str, name: str, description: str = "") -> Wave:
        name = _sanitize_name(name, _MAX_NAME_LEN)
        description = _sanitize(description, 500)
        if not name:
            raise ValueError("Wave name cannot be empty")
        wave = Wave(user_id=user_id, name=name, description=description)
        self.db.add(wave)
        self.db.commit()
        self.db.refresh(wave)
        return wave

    def get_waves(self, user_id: str) -> list[dict]:
        waves = self.db.query(Wave).filter(Wave.user_id == user_id).order_by(Wave.created_at.desc()).all()
        return [w.to_dict() for w in waves]

    def add_track_to_wave(self, wave_id: str, user_id: str, track_data: dict) -> WaveTrack | None:
        wave = self.db.query(Wave).filter(Wave.id == wave_id, Wave.user_id == user_id).first()
        if not wave:
            return None
        pos = len(wave.tracks)
        wt = WaveTrack(
            wave_id=wave_id, track_id=sanitize_track_id(str(track_data.get("id", ""))),
            source=validate_source(str(track_data.get("source", "local"))),
            title=_sanitize(str(track_data.get("name", track_data.get("title", "Unknown"))), _MAX_FIELD_LEN),
            artist=_sanitize(str(track_data.get("artist", "Unknown")), _MAX_FIELD_LEN),
            album=_sanitize(str(track_data.get("album") or ""), _MAX_FIELD_LEN),
            cover_url=track_data.get("cover_url"),
            preview_url=track_data.get("preview_url"),
            duration_ms=track_data.get("duration_ms"),
            position=pos,
        )
        self.db.add(wt)
        self.db.commit()
        self.db.refresh(wt)
        return wt

    def get_wave_tracks(self, wave_id: str, requesting_user_id: str) -> list[dict]:
        wave = self.db.query(Wave).filter(Wave.id == wave_id).first()
        if not wave or wave.user_id != requesting_user_id:
            return []
        tracks = (
            self.db.query(WaveTrack)
            .filter(WaveTrack.wave_id == wave_id)
            .order_by(WaveTrack.position)
            .all()
        )
        return [{"id": t.track_id, "name": t.title, "artist": t.artist, "album": t.album,
                 "cover_url": t.cover_url, "preview_url": t.preview_url,
                 "duration_ms": t.duration_ms, "source": t.source} for t in tracks]

    def delete_wave(self, wave_id: str, user_id: str) -> bool:
        wave = self.db.query(Wave).filter(Wave.id == wave_id, Wave.user_id == user_id).first()
        if wave:
            self.db.query(WaveTrack).filter(WaveTrack.wave_id == wave_id).delete()
            self.db.delete(wave)
            self.db.commit()
            return True
        return False

    def remove_track_from_wave(self, wave_id: str, track_id: str, user_id: str) -> bool:
        wave = self.db.query(Wave).filter(Wave.id == wave_id, Wave.user_id == user_id).first()
        if not wave:
            return False
        track_id = sanitize_track_id(track_id)
        wt = self.db.query(WaveTrack).filter(WaveTrack.wave_id == wave_id, WaveTrack.track_id == track_id).first()
        if wt:
            self.db.delete(wt)
            self.db.commit()
            return True
        return False
