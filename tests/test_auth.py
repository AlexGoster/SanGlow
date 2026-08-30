import pytest
from src.models.database import init_db, get_db_session
from src.auth.service import AuthService


def test_database_init():
    init_db()
    with get_db_session() as db:
        assert db is not None


def test_register_user():
    init_db()
    with get_db_session() as db:
        result = AuthService(db).register("testuser", "test@example.com", "SecurePass123!")
        assert result.success is True
        assert result.user is not None
        assert result.access_token is not None


def test_login_user():
    init_db()
    with get_db_session() as db:
        AuthService(db).register("logintest", "login@example.com", "SecurePass123!")
        result = AuthService(db).login("logintest", "SecurePass123!")
        assert result.success is True


def test_weak_password():
    init_db()
    with get_db_session() as db:
        result = AuthService(db).register("weak", "weak@example.com", "123")
        assert result.success is False


def test_invalid_login():
    init_db()
    with get_db_session() as db:
        result = AuthService(db).login("nobody", "wrong")
        assert result.success is False
