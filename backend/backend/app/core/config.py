from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_URL: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    MODEL_API_URL: str
    MODEL_REQUEST_TIMEOUT: int = 60
    MODEL_MAX_RETRIES: int = 3

    UPLOAD_DIR: str = "/app/uploads"
    UPLOAD_MAX_SIZE_MB: int = 10

    CORS_ALLOWED_ORIGINS: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
