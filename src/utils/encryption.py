from __future__ import annotations

import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config.settings import get_security_config


class EncryptionManager:
    def __init__(self) -> None:
        key = get_security_config().encryption_key.get_secret_value()
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"sanglow_salt_v1", iterations=480000)
        derived = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        self._fernet = Fernet(derived)

    def encrypt(self, data: str) -> str:
        return self._fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self._fernet.decrypt(encrypted_data.encode()).decode()

    @staticmethod
    def generate_key() -> str:
        return Fernet.generate_key().decode()
