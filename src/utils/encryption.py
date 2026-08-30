from __future__ import annotations

import base64
import os
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config.settings import BASE_DIR, get_security_config


class EncryptionManager:
    def __init__(self) -> None:
        key = get_security_config().encryption_key.get_secret_value()
        salt_file = BASE_DIR / "data" / ".enc_salt"
        salt_file.parent.mkdir(parents=True, exist_ok=True)
        if salt_file.exists():
            salt = salt_file.read_bytes()
        else:
            salt = os.urandom(16)
            salt_file.write_bytes(salt)
            try:
                os.chmod(salt_file, 0o600)
            except (OSError, PermissionError):
                pass
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
        derived = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        self._fernet = Fernet(derived)

    def encrypt(self, data: str) -> str:
        return self._fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self._fernet.decrypt(encrypted_data.encode()).decode()

    @staticmethod
    def generate_key() -> str:
        return Fernet.generate_key().decode()
