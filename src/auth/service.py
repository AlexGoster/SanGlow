from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.models.user import User
from .jwt_handler import JWTHandler


@dataclass
class AuthResult:
    success: bool
    user: User | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    error: str | None = None


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
            return AuthResult(success=False, error="Password must be 8+ chars with upper, lower, digit and special char")
        if self.db.query(User).filter(User.username == username).first():
            return AuthResult(success=False, error="Username already taken")
        if self.db.query(User).filter(User.email == email).first():
            return AuthResult(success=False, error="Email already registered")

        user = User(username=username, email=email, display_name=display_name or username)
        user.set_password(password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return AuthResult(success=True, user=user, access_token=self.jwt_handler.create_access_token(user.id), refresh_token=self.jwt_handler.create_refresh_token(user.id))

    def login(self, username_or_email: str, password: str) -> AuthResult:
        user = self.db.query(User).filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if not user or not user.check_password(password):
            return AuthResult(success=False, error="Invalid credentials")
        if not user.is_active:
            return AuthResult(success=False, error="Account is deactivated")
        return AuthResult(success=True, user=user, access_token=self.jwt_handler.create_access_token(user.id), refresh_token=self.jwt_handler.create_refresh_token(user.id))

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
        return (len(password) >= 8 and bool(re.search(r"[A-Z]", password))
                and bool(re.search(r"[a-z]", password)) and bool(re.search(r"\d", password))
                and bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)))
