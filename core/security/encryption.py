import base64
from cryptography.fernet import Fernet
from typing import Any, Optional
from sqlalchemy.types import TypeDecorator, String
from core.config.settings import get_settings

settings = get_settings()

# For simplicity, using Fernet which is AES-128 in CBC mode with HMAC
# Key must be 32 URL-safe base64-encoded bytes
def get_cipher() -> Fernet:
    # Ensure key is properly sized, padding or truncating as needed for Fernet
    raw_key = settings.security.secret_key.encode('utf-8')
    padded_key = base64.urlsafe_b64encode(raw_key.ljust(32)[:32])
    return Fernet(padded_key)


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
    """Custom SQLAlchemy type for transparent encryption/decryption"""
    
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
