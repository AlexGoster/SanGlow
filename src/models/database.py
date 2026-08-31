from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


_engine = None
_session_factory = None


def _get_db_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "sanglow.db"
    return Path(__file__).resolve().parent.parent.parent / "sanglow.db"


def _get_engine():
    global _engine
    if _engine is None:
        db_path = _get_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{db_path}"
        _engine = create_engine(
            url,
            echo=False,
            connect_args={"check_same_thread": False},
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )
        try:
            os.chmod(db_path, 0o600)
        except (OSError, PermissionError):
            pass
    return _engine


def _get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    sf = _get_session_factory()
    db = sf()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    sf = _get_session_factory()
    db = sf()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = _get_engine()
    Base.metadata.create_all(bind=engine)
    try:
        os.chmod(db_path, 0o600)
    except (OSError, PermissionError):
        pass
