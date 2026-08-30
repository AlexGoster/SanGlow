from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt

from config.settings import get_security_config


class JWTHandler:
    def __init__(self) -> None:
        config = get_security_config()
        self.secret_key = config.jwt_secret_key.get_secret_value()
        self.algorithm = config.jwt_algorithm
        self.expire_minutes = config.token_expire_minutes

    def create_access_token(self, user_id: str, extra_claims: dict | None = None) -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.expire_minutes)
        payload = {"sub": user_id, "iat": now, "exp": expire, "type": "access"}
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=30)
        payload = {"sub": user_id, "iat": now, "exp": expire, "type": "refresh"}
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    def decode_user_id(self, token: str) -> str | None:
        payload = self.verify_token(token)
        if payload and payload.get("type") == "access":
            return payload.get("sub")
        return None
