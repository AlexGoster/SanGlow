from __future__ import annotations

import logging
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from src.models.user import User
from src.utils.validators import sanitize_display_name
from .jwt_handler import JWTHandler
from .email_verification import generate_verification_code, send_verification_email, verify_code

logger = logging.getLogger(__name__)


@dataclass
class AuthResult:
    success: bool
    user: User | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    error: str | None = None
    requires_verification: bool = False
    verification_code: str | None = None


_login_attempts: dict[str, list[float]] = {}
_verify_attempts: dict[str, list[float]] = {}
_login_lock = threading.Lock()

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123", "monkey", "master",
    "dragon", "login", "princess", "football", "shadow", "sunshine", "trustno1",
    "iloveyou", "batman", "access", "hello", "charlie", "letmein", "welcome",
    "password1", "admin", "passw0rd", "p@ssword", "p@ssw0rd",
}


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.jwt_handler = JWTHandler()

    def register(self, username: str, email: str, password: str, display_name: str | None = None) -> AuthResult:
        if not self._validate_username(username):
            return AuthResult(success=False, error="Username must be 3-50 chars, letters and underscores only")
        if not self._validate_email(email):
            return AuthResult(success=False, error="Invalid email format")
        if not self._validate_password(password):
            return AuthResult(success=False, error="Password must be 10+ chars with upper, lower, digit and special char, not common")
        if password.lower() in COMMON_PASSWORDS:
            return AuthResult(success=False, error="Password is too common")
        if password.lower().startswith(username.lower()):
            return AuthResult(success=False, error="Password cannot start with username")
        if self.db.query(User).filter(User.username == username).first():
            return AuthResult(success=False, error="Registration failed")
        if self.db.query(User).filter(User.email == email).first():
            return AuthResult(success=False, error="Registration failed")

        code = generate_verification_code()
        safe_display = sanitize_display_name(display_name) if display_name else username
        user = User(
            username=username, email=email, display_name=safe_display,
            verification_code=code,
            verification_expires=datetime.now(timezone.utc) + timedelta(minutes=15),
        )
        user.set_password(password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        email_sent = send_verification_email(email, code, username)
        if not email_sent:
            user.email_verified = True
            user.verification_code = None
            user.verification_expires = None
            self.db.commit()
            logger.info("SMTP not configured - auto-verified user: %s", username)
            tokens = self.jwt_handler.create_access_token(user.id), self.jwt_handler.create_refresh_token(user.id)
            return AuthResult(success=True, user=user, access_token=tokens[0], refresh_token=tokens[1])
        logger.info("User registered: %s, verification email sent", username)
        return AuthResult(success=True, user=user, requires_verification=True, verification_code=code)

    def login(self, username_or_email: str, password: str) -> AuthResult:
        from config.settings import get_security_config
        cfg = get_security_config()

        key = username_or_email.lower()
        now = time.time()
        with _login_lock:
            if key in _login_attempts:
                _login_attempts[key] = [t for t in _login_attempts[key] if now - t < cfg.lockout_minutes * 60]
                if len(_login_attempts[key]) >= cfg.max_login_attempts:
                    remaining = int(cfg.lockout_minutes * 60 - (now - _login_attempts[key][0]))
                    logger.warning("Login lockout for: %s, %d seconds remaining", key, remaining)
                    return AuthResult(success=False, error=f"Too many attempts. Try again in {remaining // 60}m {remaining % 60}s")

        user = self.db.query(User).filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if not user or not user.check_password(password):
            with _login_lock:
                _login_attempts.setdefault(key, []).append(now)
                attempts_left = cfg.max_login_attempts - len(_login_attempts.get(key, []))
            logger.warning("Failed login attempt for key: %s", key)
            return AuthResult(success=False, error=f"Invalid credentials ({attempts_left} attempts left)")

        with _login_lock:
            _login_attempts.pop(key, None)

        if not user.is_active:
            return AuthResult(success=False, error="Account is deactivated")

        if not user.email_verified:
            return AuthResult(success=False, error="Please verify your email first", requires_verification=True)

        logger.info("Successful login: %s", username_or_email)
        return AuthResult(success=True, user=user, access_token=self.jwt_handler.create_access_token(user.id), refresh_token=self.jwt_handler.create_refresh_token(user.id))

    def verify_email(self, username: str, code: str) -> AuthResult:
        from config.settings import get_security_config
        cfg = get_security_config()

        key = f"verify:{username.lower()}"
        now = time.time()
        with _login_lock:
            if key in _verify_attempts:
                _verify_attempts[key] = [t for t in _verify_attempts[key] if now - t < cfg.lockout_minutes * 60]
                if len(_verify_attempts[key]) >= cfg.max_login_attempts:
                    remaining = int(cfg.lockout_minutes * 60 - (now - _verify_attempts[key][0]))
                    return AuthResult(success=False, error=f"Too many attempts. Try again in {remaining // 60}m {remaining % 60}s")

        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return AuthResult(success=False, error="User not found")
        if user.email_verified:
            return AuthResult(success=True, user=user)
        if not verify_code(user.verification_code, user.verification_expires, code):
            with _login_lock:
                _verify_attempts.setdefault(key, []).append(now)
            return AuthResult(success=False, error="Invalid or expired verification code")

        with _login_lock:
            _verify_attempts.pop(key, None)

        user.email_verified = True
        user.verification_code = None
        user.verification_expires = None
        self.db.commit()
        logger.info("Email verified for user: %s", username)
        return AuthResult(success=True, user=user, access_token=self.jwt_handler.create_access_token(user.id), refresh_token=self.jwt_handler.create_refresh_token(user.id))

    def resend_verification(self, username: str) -> AuthResult:
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return AuthResult(success=False, error="User not found")
        if user.email_verified:
            return AuthResult(success=False, error="Email already verified")
        code = generate_verification_code()
        user.verification_code = code
        user.verification_expires = datetime.now(timezone.utc) + timedelta(minutes=15)
        self.db.commit()
        email_sent = send_verification_email(user.email, code, user.username)
        if not email_sent:
            user.email_verified = True
            user.verification_code = None
            user.verification_expires = None
            self.db.commit()
            tokens = self.jwt_handler.create_access_token(user.id), self.jwt_handler.create_refresh_token(user.id)
            return AuthResult(success=True, user=user, access_token=tokens[0], refresh_token=tokens[1], verification_code=code)
        logger.info("Verification email resent to %s", user.email)
        return AuthResult(success=True, user=user, verification_code=code)

    def change_password(self, user_id: str, current_password: str, new_password: str) -> AuthResult:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return AuthResult(success=False, error="User not found")
        if not user.check_password(current_password):
            return AuthResult(success=False, error="Current password is incorrect")
        if current_password == new_password:
            return AuthResult(success=False, error="New password must be different from current")
        if not self._validate_password(new_password):
            return AuthResult(success=False, error="Password must be 10+ chars with upper, lower, digit and special char")
        if new_password.lower() in COMMON_PASSWORDS:
            return AuthResult(success=False, error="Password is too common")
        user.set_password(new_password)
        self.db.commit()
        logger.info("Password changed for user: %s", user.username)
        return AuthResult(success=True, user=user)

    def get_current_user(self, token: str) -> User | None:
        user_id = self.jwt_handler.decode_user_id(token)
        if not user_id:
            return None
        return self.db.query(User).filter(User.id == user_id).first()

    def _validate_username(self, username: str) -> bool:
        return 3 <= len(username) <= 50 and bool(re.match(r"^[a-zA-Z0-9_]+$", username))

    def _validate_email(self, email: str) -> bool:
        return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))

    def _validate_password(self, password: str) -> bool:
        from config.settings import get_security_config
        cfg = get_security_config()
        if len(password) > cfg.max_password_length:
            return False
        return (len(password) >= 10 and bool(re.search(r"[A-Z]", password))
                and bool(re.search(r"[a-z]", password)) and bool(re.search(r"\d", password))
                and bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)))
