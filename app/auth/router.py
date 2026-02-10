# app/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, Query, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from .schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    TokenPairResponse,
    MessageResponse,
    PasswordResetRequest,
    PasswordResetConfirmRequest
)
from .service import AuthService
from .repository import AuthRepository
from .exceptions import AuthError, ValidationError
from app.config.database import get_session

from uuid import UUID
from .security import get_current_user_id




router = APIRouter()


def get_service():
    return AuthService(AuthRepository())


@router.post("/register", response_model=MessageResponse)
def register(
            data: RegisterRequest,
            session: Session = Depends(get_session),
            service: AuthService = Depends(get_service),
            ):
    try:
        service.register(session, data)
        return MessageResponse(message="Проверьте почту для подтверждения email")


    except ValidationError as e:
        raise HTTPException(
            status_code=410 if e.code == "INVALID_TOKEN" else 400,
            detail={
                "code": e.code,
                "message": e.message,
                "field": e.field,
            },
        )

@router.post("/login", response_model=TokenPairResponse) # Вход через форму с помощью OAuth2PasswordRequestForm
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
    service: AuthService = Depends(get_service),
):
    try:
        return service.login(
            session,
            email=form_data.username,  # ← email здесь
            password=form_data.password,
        )
    except AuthError as e:
        raise HTTPException(status_code=400, detail=e.message)

@router.post("/login/json", response_model=TokenPairResponse) # Вход через json для апи
def login_json(
    data: LoginRequest,
    session: Session = Depends(get_session),
    service: AuthService = Depends(get_service),
):
    try:
        return service.login(session, data.email, data.password)
    except AuthError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(
    data: RefreshRequest,
    session: Session = Depends(get_session),
    service: AuthService = Depends(get_service),
):
    try:
        return service.refresh(session, data.refresh_token)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=e.message)


@router.post("/logout-all", response_model=MessageResponse)
def logout_all(
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session),
    service: AuthService = Depends(get_service),
):
    service.logout_all(session, user_id)
    return {"message": "Вы вышли со всех устройств"}


@router.get("/confirm-email", response_model=MessageResponse)
def confirm_email(
    token: str = Query(...),
    session: Session = Depends(get_session),
    service: AuthService = Depends(get_service),
):
    try:
        service.confirm_email(session, token)
        return MessageResponse(message="Email подтверждён")

    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": e.code,
                "message": e.message,
                "field": e.field,
            },
        )


@router.post("/password-reset/request", response_model=MessageResponse)
def password_reset_request(
    data: PasswordResetRequest,
    session: Session = Depends(get_session),
    service: AuthService = Depends(get_service),
):
    service.request_password_reset(session, data.email)
    return MessageResponse(
        message="Если email существует, инструкция отправлена"
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
def password_reset_confirm(
    data: PasswordResetConfirmRequest,
    session: Session = Depends(get_session),
    service: AuthService = Depends(get_service),
):
    service.reset_password(
        session,
        data.token,
        data.new_password,
        data.confirm_password,
        data.email,
    )
    return MessageResponse(message="Пароль успешно изменён")