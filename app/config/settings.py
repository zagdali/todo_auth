from pydantic_settings import BaseSettings

# Настройки приложения получаются из файла .env! Получить адрес базы данных settings.DATABASE_URL
class Settings(BaseSettings):
   DATABASE_URL: str
   POSTGRES_USER : str
   POSTGRES_PASSWORD : str
   POSTGRES_DB : str

   JWT_SECRET: str
   JWT_ALGORITHM: str = "HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

   DEBUG: bool
   ENVIRONMENT: str

   # в будушем можно добавить
   REDIS_URL : str
   MINIO_ENDPOINT : str
   MINIO_ACCESS_KEY : str
   MINIO_SECRET_KEY : str
   MINIO_BUCKET : str



   class Config:
      env_file = "app/config/.env"


settings = Settings()