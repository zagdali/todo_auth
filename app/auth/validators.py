# app/auth/validators.py

from app.config.settings import settings

from .exceptions import ValidationError

import re


def validate_password(password: str, email: str):
    # обязательность
    if not password:
        raise ValidationError(
            code="PASSWORD_REQUIRED",
            message="Пароль обязателен к заполнению",
            field="password",
        )

    # длина
    if not (settings.PASSWORD_MIN_LENGTH <= len(password) <= settings.PASSWORD_MAX_LENGTH):
        raise ValidationError(
            code="PASSWORD_LENGTH",
            message=(
                f"Пароль должен быть длиной от "
                f"{settings.PASSWORD_MIN_LENGTH} до {settings.PASSWORD_MAX_LENGTH} символов"
            ),
            field="password",
        )

    # запрещённые символы
    if re.search(settings.FORBIDDEN_PASSWORD_CHARS, password):
        raise ValidationError(
            code="PASSWORD_FORBIDDEN_CHARS",
            message="Пароль содержит недопустимый символ",
            field="password",
        )

    # обязательные символы
    if not re.search(settings.PASSWORD_REQUIRED_REGEX["uppercase"], password):
        raise ValidationError(
            code="PASSWORD_UPPERCASE",
            message="Пароль должен содержать минимум одну заглавную букву (A–Z)",
            field="password",
        )

    if not re.search(settings.PASSWORD_REQUIRED_REGEX["lowercase"], password):
        raise ValidationError(
            code="PASSWORD_LOWERCASE",
            message="Пароль должен содержать минимум одну строчную букву (a–z)",
            field="password",
        )

    if not re.search(settings.PASSWORD_REQUIRED_REGEX["digit"], password):
        raise ValidationError(
            code="PASSWORD_DIGIT",
            message="Пароль должен содержать минимум одну цифру (0–9)",
            field="password",
        )

    if not re.search(settings.PASSWORD_REQUIRED_REGEX["special"], password):
        raise ValidationError(
            code="PASSWORD_SPECIAL",
            message="Пароль должен содержать минимум один специальный символ",
            field="password",
        )

    # email в пароле не нужна проверка так как ниже проверяем части email


    # проверка 2 частей email перед и после @
    local_part, domain_part = email.lower().split("@")

    password_lower = password.lower()

    # --- часть ДО @ ---
    local_chunks = re.split(r"[.\-_]", local_part)

    for chunk in local_chunks:
        if len(chunk) >= 3 and chunk in password_lower: # чтобы не ловить мусор из 2 букв
            raise ValidationError(
                code="PASSWORD_CONTAINS_EMAIL_PART",
                message=(
                    "Пароль не должен содержать часть email "
                    "до символа @"
                ),
                field="password",
            )

    # --- часть ПОСЛЕ @ ---
    domain_chunks = re.split(r"[.\-_]", domain_part)

    for chunk in domain_chunks:
        if len(chunk) >= 4 and chunk in password_lower: # чтобы не ловить мусор вроде jo, gm, ru, etc, com
            raise ValidationError(
                code="PASSWORD_CONTAINS_EMAIL_DOMAIN",
                message=(
                    "Пароль не должен содержать часть email "
                    "после символа @"
                ),
                field="password",
            )
