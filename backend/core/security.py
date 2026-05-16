"""
Функции безопасности: хеширование паролей и работа с JWT токенами
"""
from datetime import datetime, timedelta, UTC
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.core.config import settings

# Контекст для хеширования паролей (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Хеширование пароля с использованием bcrypt

    Args:
        password: Пароль в открытом виде

    Returns:
        Хеш пароля
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка пароля с хешем

    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Хеш пароля из БД

    Returns:
        True если пароль совпадает, иначе False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создание JWT токена доступа

    Args:
        data: Данные для кодирования в токен (обычно user_id, login)
        expires_delta: Время жизни токена (по умолчанию из настроек)

    Returns:
        JWT токен в виде строки
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Декодирование JWT токена

    Args:
        token: JWT токен

    Returns:
        Словарь с данными из токена или None если токен невалидный
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
