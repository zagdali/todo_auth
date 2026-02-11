# app/auth/service.py
from datetime import datetime, timezone
from sqlmodel import Session
from uuid import UUID
from .repository import AuthRepository
from .schemas import RegisterRequest
from app.models.user import User, Tokens
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    generate_token,
    token_expiration,
)
from app.config.settings import settings

from .validators import validate_password
from .exceptions import InvalidCredentials, EmailAlreadyExists, EmailNotVerified, ValidationError
from .templates import email_confirmation, password_reset

# Импорт задач Celery с обработкой ошибок
try:
    from app.tasks.email_tasks import send_email_confirmation, send_password_reset
    CELERY_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    CELERY_AVAILABLE = False
    print("[WARNING] Celery not available. Email sending will be synchronous.")



class AuthService:

    def __init__(self, repo: AuthRepository):
        self.repo = repo

    def register(self, session, data):

        if self.repo.get_user_by_email(session, data.email):
            raise ValidationError(
                "EMAIL_EXISTS",
                "Пользователь с таким email уже существует",
                "email",
            )
        validate_password(data.password, data.email)

        if data.password != data.password_confirm:
            raise ValidationError(
                code="PASSWORD_MISMATCH",
                message=(
                    "Пароли не совпадают. "
                    "Пожалуйста, введите одинаковые пароли."
                ),
                field="password_confirm",
            )
        #  создать пользователя (is_active=False)

        user = self.repo.create_user(
            session,
            User(
                email=data.email,
                password_hash=hash_password(data.password),
                is_active=False,
            )
        )

        #  создать токен
        token = self.repo.create_token(
            session,
            user.id,
            settings.EMAIL_CONFIRM_TOKEN_TYPE,
            token_expiration(24),
        )

        # отправить письмо через Celery (или синхронно при ошибке)
        self._send_confirmation_email(user.email, token.token)

        return {"message": "Проверьте почту для подтверждения"}

    def _send_confirmation_email(self, email: str, token: str):
        """Отправка письма подтверждения с обработкой ошибок"""
        if CELERY_AVAILABLE:
            try:
                send_email_confirmation.delay(email, token)
                print(f"[CELERY] Email task queued for {email}")
            except Exception as e:
                print(f"[CELERY ERROR] Failed to queue email task: {e}")
                # Отправляем синхронно как резервный вариант
                self._send_email_sync(email, token, "confirmation")
        else:
            print(f"[SYNC] Sending email synchronously to {email}")
            self._send_email_sync(email, token, "confirmation")

    def _send_password_reset_email(self, email: str, token: str):
        """Отправка письма сброса пароля с обработкой ошибок"""
        if CELERY_AVAILABLE:
            try:
                send_password_reset.delay(email, token)
                print(f"[CELERY] Password reset task queued for {email}")
            except Exception as e:
                print(f"[CELERY ERROR] Failed to queue password reset task: {e}")
                self._send_email_sync(email, token, "password_reset")
        else:
            print(f"[SYNC] Sending password reset email synchronously to {email}")
            self._send_email_sync(email, token, "password_reset")

    def _send_email_sync(self, email: str, token: str, email_type: str):
        """Синхронная отправка письма (резервный вариант)"""
        try:
            from app.tasks.email_tasks import _email

            # Генерируем ссылки
            if email_type == "confirmation":
                confirm_url = f"http://localhost:8000/auth/confirm-email?token={token}"
                template = email_confirmation(confirm_url)
            else:
                reset_url = f"http://localhost:8000/auth/password-reset/confirm?token={token}"
                template = password_reset(reset_url)

            # Отправляем письмо
            _email(
                email,
                template.subject,
                template.html,
                template.text
            )
            print(f"[SYNC EMAIL SENT] To: {email}")

        except Exception as e:
            print(f"[SYNC EMAIL ERROR] Failed to send email to {email}: {e}")
            # Не выбрасываем исключение, чтобы не сломать регистрацию



    def confirm_email(self, session, token_str: str):
        token = self.repo.get_valid_token(session, token_str, settings.EMAIL_CONFIRM_TOKEN_TYPE)

        if not token:
            raise ValidationError(
                "INVALID_TOKEN",
                "Ссылка недействительна или устарела",
                "token",
            )

        user = session.get(User, token.user_id)
        user.is_active = True
        token.is_used = True

        session.commit()
        return {"message": "Email подтверждён"}

# запрос на сброс пароля
    def request_password_reset(self, session, email: str):
        user = self.repo.get_user_by_email(session, email)
        if not user:
            return {"message": "Такого пользователя не существует, проверьте email"}

        token = self.repo.create_token(
            session,
            user.id,
            settings.PASSWORD_RESET_TOKEN_TYPE,
            token_expiration(1),
        )

        self._send_password_reset_email(user.email, token.token)

        return {"message": "Если email существует, инструкция отправлена"}

# установка нового пароля
    def reset_password(self, session, token_str: str, new_password: str, confirm_password: str, email: str):

        token = self.repo.get_valid_token(session, token_str, settings.PASSWORD_RESET_TOKEN_TYPE)
        if not token:
            raise ValidationError(
                "INVALID_TOKEN",
                "Ссылка недействительна или устарела",
                "token",
            )
        if new_password != confirm_password:
            raise ValidationError(
                code="PASSWORD_MISMATCH",
                message="Пароли не совпадают",
                field="confirm_password",
            )

        validate_password(new_password, email)

        user = session.get(User, token.user_id)
        user.password_hash = hash_password(new_password)
        token.is_used = True

        session.commit()
        return {"message": "Пароль успешно изменён"}

    def login(self, session: Session, email: str, password: str):
        user = self.repo.get_user_by_email(session, email)

        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentials()

        if not user.is_active:
            raise EmailNotVerified()

        return self._issue_token_pair(session, user)

    def refresh(self, session: Session, refresh_token: str):
        token_hash = hash_refresh_token(refresh_token)

        stored = self.repo.get_refresh_token(session, token_hash)
        if not stored:
            raise InvalidCredentials()

        # ротация токенов
        self.repo.revoke_refresh_token(session, stored)

        user = session.get(User, stored.user_id)
        return self._issue_token_pair(session, user)

    def _issue_token_pair(self, session: Session, user: User):
        access = create_access_token(user.id)
        refresh = create_refresh_token()

        refresh_db = Tokens(
            user_id=user.id,
            token=None,
            token_type=settings.REFRESH_TOKEN_TYPE,
            token_hash=hash_refresh_token(refresh),
            expires_at=datetime.now(timezone.utc) + settings.REFRESH_TOKEN_TTL,
        )

        self.repo.save_refresh_token(session, refresh_db)

        return {
            "access_token": access,
            "refresh_token": refresh,
        }

    def logout_all(self, session: Session, user_id: UUID):
        # если user_id валиден — просто отзываем все refresh
        self.repo.revoke_all_refresh_tokens(session, user_id)

        return {"message": "Вы вышли со всех устройств"}
