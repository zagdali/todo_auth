# app/auth/security.py
import hashlib
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from secrets import token_urlsafe
from app.config.settings import settings




pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash_: str) -> bool:
    return pwd_context.verify(password, hash_)


def create_access_token(user_id: UUID) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + settings.ACCESS_TOKEN_TTL,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token() -> str:
    return token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def generate_token() -> str: # для емаил токенов
    return str(uuid4())


def token_expiration(hours: int) -> datetime: # для емаил токенов
    return datetime.utcnow() + timedelta(hours=hours)