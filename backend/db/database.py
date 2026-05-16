"""
Конфигурация подключения к БД PostgreSQL
SQLAlchemy 2.0 синхронный стиль с psycopg2
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from backend.core.config import settings

# URL для psycopg2
DATABASE_URL = settings.DATABASE_URL

# Синхронный движок
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Логирование SQL-запросов в dev режиме
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=5,
    max_overflow=10,
)

# Фабрика синхронных сессий
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# Базовый класс для ORM моделей
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency для получения сессии БД
    Используется в FastAPI эндпоинтах через Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
