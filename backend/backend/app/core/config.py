from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    # Database
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Redis
    REDIS_URL: str

    # Security / Auth
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Model gateway / provider selection
    MODEL_PROVIDER: str = "mock"  # e.g. glm52, openai, vllm, ollama, sglang, generic, mock
    MODEL_PROVIDER_FALLBACKS: str = ""  # comma separated fallback provider keys
    MODEL_API_URL: str = ""  # generic URL fallback if provider-specific URL not provided
    MODEL_API_KEY: str = ""  # generic API key fallback
    MODEL_NAME: str = ""
    MODEL_REQUEST_TIMEOUT: int = 60
    MODEL_MAX_RETRIES: int = 3

    # Uploads
    UPLOAD_DIR: str = "/app/uploads"
    UPLOAD_MAX_SIZE_MB: int = 10

    # CORS
    CORS_ALLOWED_ORIGINS: str = ""

    # Convenience toggles
    AUTO_CREATE_DB_TABLES: bool = False  # set true for first-run convenience, false in production

    class Config:
        env_file = ".env"

settings = Settings()
