from datetime import datetime, timedelta, timezone
from typing import Optional, Set
from uuid import uuid4

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config.settings import get_settings
from core.exceptions import AuthenticationError

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

_token_blacklist: Set[str] = set()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(seconds=settings.security.access_token_expire)
    to_encode.update({
        "exp": expire,
        "iat": now,
        "jti": str(uuid4()),
    })
    encoded_jwt = jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({
        "exp": expire,
        "iat": now,
        "jti": str(uuid4()),
        "type": "refresh",
    })
    encoded_jwt = jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)
    return encoded_jwt


def revoke_token(jti: str) -> None:
    _token_blacklist.add(jti)


def is_token_revoked(jti: str) -> bool:
    return jti in _token_blacklist


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.algorithm])
        jti = payload.get("jti")
        if jti and is_token_revoked(jti):
            raise AuthenticationError("Token has been revoked")
        return payload
    except JWTError as e:
        raise AuthenticationError("Could not validate credentials") from e


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    return decode_token(token)
