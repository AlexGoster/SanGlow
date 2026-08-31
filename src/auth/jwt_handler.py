from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from config.settings import get_security_config

logger = logging.getLogger(__name__)

ALLOWED_ALGORITHMS = {"HS256", "HS384", "HS512"}
BLOCKED_ALGORITHMS = {"none", "None", "NONE", "HS1", "HS0"}


class JWTHandler:
    def __init__(self) -> None:
        config = get_security_config()
        self.secret_key = config.jwt_secret_key.get_secret_value()
        self.algorithm = config.jwt_algorithm
        self.access_expire_minutes = 15
        self.refresh_expire_days = 7
        self._validate_algorithm()

    def _validate_algorithm(self) -> None:
        if self.algorithm in BLOCKED_ALGORITHMS:
            raise ValueError(f"Blocked algorithm: {self.algorithm}")
        if self.algorithm not in ALLOWED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

    def create_access_token(self, user_id: str, extra_claims: dict | None = None) -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_expire_minutes)
        jti = secrets.token_urlsafe(32)
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": expire,
            "nbf": now,
            "type": "access",
            "jti": jti,
            "iss": "sanglow",
            "aud": "sanglow-client",
        }
        if extra_claims:
            safe_claims = {k: v for k, v in extra_claims.items() if k in ("role", "name")}
            payload.update(safe_claims)
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_expire_days)
        jti = secrets.token_urlsafe(32)
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": expire,
            "nbf": now,
            "type": "refresh",
            "jti": jti,
            "iss": "sanglow",
            "aud": "sanglow-client",
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer="sanglow",
                audience="sanglow-client",
                options={"require": ["exp", "sub", "iss", "aud", "type"]},
            )
            if payload.get("alg") in BLOCKED_ALGORITHMS:
                logger.warning("Blocked algorithm in token payload: %s", payload.get("alg"))
                return None
            return payload
        except jwt.ExpiredSignatureError:
            logger.debug("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token: %s", e)
            return None

    def decode_user_id(self, token: str) -> str | None:
        payload = self.verify_token(token)
        if payload and payload.get("type") == "access":
            return payload.get("sub")
        return None

    def get_token_jti(self, token: str) -> str | None:
        payload = self.verify_token(token)
        return payload.get("jti") if payload else None
