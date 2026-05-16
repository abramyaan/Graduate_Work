"""
Конфигурация подключения к БД PostgreSQL
SQLAlchemy 2.0 асинхронный стиль с asyncpg
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base

from backend.core.config import settings

# URL для asyncpg
DATABASE_URL = settings.DATABASE_URL

# Асинхронный движок
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Логирование SQL-запросов в dev режиме
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=5,
    max_overflow=10,
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Базовый класс для ORM моделей
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения асинхронной сессии БД
    Используется в FastAPI эндпоинтах через Depends(get_db)

    Пример использования:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Синхронная версия для скриптов (create_admin.py, init_data.py)
# Используем pg8000 драйвер для синхронных операций
from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy.orm import sessionmaker, Session

# Преобразуем async URL в sync URL с pg8000
SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "+pg8000")

sync_engine = create_sync_engine(
    SYNC_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


def get_sync_db() -> Session:
    """
    Синхронная версия для использования в скриптах
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
