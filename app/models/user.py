# app.models.user.py
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from uuid import UUID, uuid4

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=254)
    hashed_password: str
    is_active: bool = False
    is_archived: bool = False
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))