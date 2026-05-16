"""
Dependencies для FastAPI эндпоинтов
Получение текущего пользователя, проверка прав доступа и т.д.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.models.models import UserAccount
from backend.core.security import decode_access_token

# OAuth2 схема для извлечения токена из заголовка Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserAccount:
    """
    Dependency для получения текущего аутентифицированного пользователя

    Извлекает JWT токен из заголовка Authorization,
    декодирует его и возвращает пользователя из БД

    Args:
        token: JWT токен из заголовка Authorization: Bearer <token>
        db: Асинхронная сессия БД

    Returns:
        Модель UserAccount текущего пользователя

    Raises:
        HTTPException 401: Если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Декодирование токена
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Извлечение user_id из токена
    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    # Получение пользователя из БД
    stmt = select(UserAccount).where(UserAccount.user_id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: UserAccount = Depends(get_current_user)
) -> UserAccount:
    """
    Dependency для получения активного пользователя

    Дополнительная проверка на случай если в будущем добавится поле is_active

    Args:
        current_user: Текущий пользователь из get_current_user

    Returns:
        Модель UserAccount текущего активного пользователя

    Raises:
        HTTPException 400: Если пользователь неактивен (в будущем)
    """
    # TODO: Добавить проверку is_active если это поле появится в модели
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Пользователь деактивирован")

    return current_user


async def require_admin(
    current_user: UserAccount = Depends(get_current_user)
) -> UserAccount:
    """
    Dependency для проверки прав администратора

    Args:
        current_user: Текущий пользователь

    Returns:
        Модель UserAccount если пользователь - администратор

    Raises:
        HTTPException 403: Если пользователь не администратор
    """
    # role_id = 1 это Администратор согласно db/schema.sql
    if current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль Администратора"
        )
    return current_user


async def require_recruiter_or_admin(
    current_user: UserAccount = Depends(get_current_user)
) -> UserAccount:
    """
    Dependency для проверки прав рекрутера или администратора

    Args:
        current_user: Текущий пользователь

    Returns:
        Модель UserAccount если пользователь - рекрутер или администратор

    Raises:
        HTTPException 403: Если недостаточно прав
    """
    # role_id: 1 = Администратор, 2 = Рекрутер
    if current_user.role_id not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль Администратора или Рекрутера"
        )
    return current_user
