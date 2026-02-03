#app.config.auth.py - Регистрация пользователя

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.schemas.auth import RegisterSchema
from app.models.user import User
from app.core.database import get_session
from app.core.security import hash_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=201)
def register(data: RegisterSchema, session: Session = Depends(get_session)):
    email = data.email.lower()

    existing = session.exec(
        select(User).where(User.email == email)
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Проверьте введенные данные")

    user = User(
        email=email,
        hashed_password=hash_password(data.password),
        is_active=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # email confirmation будет тут (Celery)

    return {"message": "Письмо с подтверждением отправлено"}
