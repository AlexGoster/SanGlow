from __future__ import annotations

import json
import logging
import secrets
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt

from config.settings import DATA_DIR, get_security_config

logger = logging.getLogger(__name__)

ALLOWED_ALGORITHMS = {"HS256", "HS384", "HS512"}
BLOCKED_ALGORITHMS = {"none", "None", "NONE", "HS1", "HS0"}


class _TokenBlacklist:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._blacklist_file = DATA_DIR / ".token_blacklist.json"
        self._blacklist_file.parent.mkdir(parents=True, exist_ok=True)
        self._jti_set: set[str] = set()
        self._load()

    def _load(self) -> None:
        try:
            if self._blacklist_file.exists():
                data = json.loads(self._blacklist_file.read_text(encoding="utf-8"))
                entries = data.get("entries", data.get("jti", []))
                if entries and isinstance(entries[0], dict):
                    self._jti_set = {e["j"] for e in entries}
                else:
                    self._jti_set = set(entries) if entries else set()
        except Exception:
            self._jti_set = set()

    def _save(self) -> None:
        try:
            now = datetime.now(timezone.utc).timestamp()
            entries = [{"j": jti, "t": now} for jti in self._jti_set]
            self._blacklist_file.write_text(
                json.dumps({"entries": entries}), encoding="utf-8"
            )
            try:
                import os
                os.chmod(self._blacklist_file, 0o600)
            except (OSError, PermissionError):
                pass
        except Exception as e:
            logger.error("Failed to save token blacklist: %s", e)

    def add(self, jti: str) -> None:
        with self._lock:
            self._jti_set.add(jti)
            self._save()

    def contains(self, jti: str) -> bool:
        with self._lock:
            return jti in self._jti_set

    def cleanup(self, max_age_hours: int = 24) -> None:
        with self._lock:
            try:
                data = json.loads(self._blacklist_file.read_text(encoding="utf-8")) if self._blacklist_file.exists() else {}
                jti_with_time = data.get("entries", [])
                now = datetime.now(timezone.utc).timestamp()
                cutoff = now - (max_age_hours * 3600)
                valid = [e for e in jti_with_time if e.get("t", 0) > cutoff]
                self._jti_set = {e["j"] for e in valid}
                self._save()
            except Exception as e:
                logger.error("Failed to cleanup token blacklist: %s", e)


_blacklist = _TokenBlacklist()


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
                options={"require": ["exp", "sub", "iss", "aud", "type", "jti"]},
            )
            if payload.get("alg") in BLOCKED_ALGORITHMS:
                logger.warning("Blocked algorithm in token payload: %s", payload.get("alg"))
                return None
            jti = payload.get("jti")
            if jti and _blacklist.contains(jti):
                logger.warning("Revoked token used: %s", jti)
                return None
            return payload
        except jwt.ExpiredSignatureError:
            logger.debug("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token: %s", e)
            return None

    def revoke_token(self, token: str) -> bool:
        payload = self.verify_token(token)
        if payload and payload.get("jti"):
            _blacklist.add(payload["jti"])
            return True
        return False

    def decode_user_id(self, token: str) -> str | None:
        payload = self.verify_token(token)
        if payload and payload.get("type") == "access":
            return payload.get("sub")
        return None

    def get_token_jti(self, token: str) -> str | None:
        payload = self.verify_token(token)
        return payload.get("jti") if payload else None
