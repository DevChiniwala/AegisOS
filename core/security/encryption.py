import base64
from typing import Any, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from sqlalchemy.types import String, TypeDecorator

from core.config.settings import get_settings

_cipher_instance: Optional[Fernet] = None


def get_cipher() -> Fernet:
    global _cipher_instance
    if _cipher_instance is not None:
        return _cipher_instance

    settings = get_settings()
    raw_key = settings.security.secret_key.encode('utf-8')

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"aegisos-encryption-salt-v1",
        info=b"aegisos-field-encryption",
    )
    derived_key = hkdf.derive(raw_key)
    fernet_key = base64.urlsafe_b64encode(derived_key)
    _cipher_instance = Fernet(fernet_key)
    return _cipher_instance


def encrypt_field(data: str) -> str:
    if not data:
        return data
    cipher = get_cipher()
    return cipher.encrypt(data.encode('utf-8')).decode('utf-8')


def decrypt_field(encrypted_data: str) -> str:
    if not encrypted_data:
        return encrypted_data
    cipher = get_cipher()
    return cipher.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')


class EncryptedString(TypeDecorator):
    """Custom SQLAlchemy type for transparent encryption/decryption."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value: Optional[str], dialect: Any) -> Optional[str]:
        if value is None:
            return None
        return encrypt_field(value)

    def process_result_value(self, value: Optional[str], dialect: Any) -> Optional[str]:
        if value is None:
            return None
        return decrypt_field(value)
