"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения"""

    # База данных
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/resume_db"

    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ML-модель
    MODEL_PATH: str = "ml/models/finetuned_model"

    # Файловые хранилища
    FILES_RESUMES_PATH: str = "files/resumes"
    FILES_MODELS_PATH: str = "files/models"
    FILES_REPORTS_PATH: str = "files/reports"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Настройка pydantic-settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Это ключевая строка: игнорировать VITE_ и другие лишние переменные
    )


settings = Settings()