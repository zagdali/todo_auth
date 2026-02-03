from datetime import timedelta, datetime, timezone
import os
from jose import jwt
from jose.exceptions import JWTError  # импорт исключения
from app.models.user import User
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, field_validator # pydantic версии 2 нужен
import re

# Проверка если тест то из fake
# if os.getenv("CRYPTID_UNIT_TEST"):
#     from fake import user as data
# else:
#     from data import user as data

# --- Настройки аутентификации


# ⚠️⚠️⚠️ ВАЖНО: потом убрать переменную в окружение .env
SECRET_KEY = os.getenv("SECRET_KEY", "keep-it-secret-keep-it-safe")
ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hash: str) -> bool:
    """Проверка соответствия открытого пароля хешу из БД"""
    return pwd_context.verify(plain, hash)


def get_hash(plain: str) -> str:
    """Генерация хеша для открытого пароля"""
    return pwd_context.hash(plain)


def get_jwt_username(token: str) -> str | None:
    """Извлечение имени пользователя (sub) из JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        # Явная проверка на строку и непустое значение
        if isinstance(username, str) and username.strip():
            return username.strip()
        return None
    except JWTError:
        return None


def get_current_user(token: str) -> User | None:
    """Получение объекта пользователя по токену"""
    if not (username := get_jwt_username(token)):
        return None
    return lookup_user(username)


def lookup_user(username: str) -> User | None:
    """Поиск пользователя по имени. """
    try:
        return data.get_one(username)  # Использование модуля data для доступа к данным
    except (AttributeError, KeyError, ValueError):
        return None


def auth_user(name: str, plain: str) -> User | None:
    """Аутентификация пользователя по имени и паролю"""
    user = lookup_user(name)
    if not user or not verify_password(plain, user.hash):  # Проверка пароля из БД
        return None
    return user


def create_access_token(to_encode: dict, expires: timedelta | None = None) -> str:  # Параметр переименован
    """Генерация JWT-токена."""
    payload = to_encode.copy()
    now = datetime.now(timezone.utc)

    if expires is None:  # Явная проверка на None (timedelta(0) — валидное значение)
        expires = timedelta(minutes=15)

    payload.update({
        "exp": now + expires,
        "iat": now  # Добавлено время выдачи для лучшей аудитории
    })

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# --- CRUD-операции для работы с пользователями
def get_all() -> list[User]:
    return data.get_all()


def get_one(name: str) -> User:
    return data.get_one(name)


def create(user: User) -> User:
    return data.create(user)


def modify(name: str, user: User) -> User:
    return data.modify(name, user)


def delete(name: str) -> None:
    return data.delete(name)





# валидация email и пароля

PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!$%^*()_+]).{12,100}$"
)

FORBIDDEN = r"[\'\"\\\/;#<>@&]"

class RegisterSchema(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if re.search(FORBIDDEN, v):
            raise ValueError("Пароль содержит недопустимый символ")
        if not PASSWORD_REGEX.match(v):
            raise ValueError("Пароль не соответствует требованиям безопасности")
        return v

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v, info):
        if v != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return v
