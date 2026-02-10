# app/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from datetime import timedelta
import warnings


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

if not ENV_PATH.exists():
    warnings.warn(
        f".env file not found at {ENV_PATH}. "
        "Settings will be loaded from system environment variables only.",
        UserWarning
    )


class Settings(BaseSettings):
    # -------------------- Database --------------------
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # -------------------- JWT --------------------
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # -------------------- Token types --------------------
    EMAIL_CONFIRM_TOKEN_TYPE: str = "email_confirm"
    PASSWORD_RESET_TOKEN_TYPE: str = "password_reset"
    REFRESH_TOKEN_TYPE: str = "refresh_token"

    # -------------------- Password policy --------------------
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_MAX_LENGTH: int = 100

    PASSWORD_REQUIRED_REGEX: dict = {
        "uppercase": r"[A-Z]",
        "lowercase": r"[a-z]",
        "digit": r"\d",
        "special": r"[!$%^*()_+=\-]",
    }

    FORBIDDEN_PASSWORD_CHARS: str = r"(\'|\"|\\|\/|;|--|#|<|>|&|@)"

    # -------------------- App --------------------
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # -------------------- Email --------------------
    EMAIL_HOST: str = ""
    EMAIL_PORT: int = 587
    EMAIL_HOST_USER: str = ""
    EMAIL_HOST_PASSWORD: str = ""
    EMAIL_USE_TLS: bool = True
    EMAIL_FROM: str = ""

    # -------------------- Redis --------------------
    REDIS_URL: str = "redis://redis:6379/0"

    # -------------------- Derived values --------------------
    @property
    def ACCESS_TOKEN_TTL(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def REFRESH_TOKEN_TTL(self) -> timedelta:
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )


settings = Settings()
