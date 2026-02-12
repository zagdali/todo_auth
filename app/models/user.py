#app/models/user.py
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "user"
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    email: str = Field(index=True, unique=True)
    password_hash: str

    is_active: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Tokens(SQLModel, table=True):
    __tablename__ = "tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")

    token: Optional[str] = Field(default=None, index=True)
    token_hash: Optional[str] = Field(default=None, index=True)  # Для refresh токенов
    token_type: str  # "email_confirm", "password_reset", "refresh_token"

    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_used: bool = Field(default=False)  # Для одноразовых токенов
    revoked_at: datetime | None = None  # Для refresh токенов