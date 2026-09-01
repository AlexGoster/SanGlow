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
        assert result.requires_verification is True
        code = result.user.verification_code
        assert code is not None
        verify_result = AuthService(db).verify_email("testuser", code)
        assert verify_result.success is True
        assert verify_result.access_token is not None


def test_login_user():
    init_db()
    with get_db_session() as db:
        reg = AuthService(db).register("logintest", "login@example.com", "SecurePass123!")
        AuthService(db).verify_email("logintest", reg.user.verification_code)
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
