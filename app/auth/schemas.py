# app/auth/schemas.py
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., example="94433@mail.ru")
    password: str = Field(..., example="!MyPassword123")
    password_confirm: str = Field(..., example="!MyPassword123")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="94433@mail.ru")
    password: str = Field(..., example="!MyPassword123")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., example="94433@mail.ru")

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str
    email: EmailStr


class MessageResponse(BaseModel):
    message: str