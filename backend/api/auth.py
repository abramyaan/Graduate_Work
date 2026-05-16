"""
Роутер авторизации
Эндпоинты для логина и получения JWT токена
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db.database import get_db
from backend.models.models import UserAccount
from backend.schemas.user_account import UserLogin, Token, UserAccountWithRole
from backend.core.security import verify_password, create_access_token
from backend.core.dependencies import get_current_user

router = APIRouter()


@router.post("/login", response_model=Token, summary="Вход в систему")
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Аутентификация пользователя и выдача JWT токена

    Принимает:
    - **login**: Логин пользователя (минимум 5 символов)
    - **password**: Пароль пользователя (минимум 8 символов)

    Возвращает:
    - **access_token**: JWT токен для доступа к API
    - **token_type**: Тип токена (bearer)

    Коды ошибок:
    - 401: Неверный логин или пароль
    """
    # Поиск пользователя по логину
    stmt = select(UserAccount).where(UserAccount.login == credentials.login)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # Проверка существования пользователя
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверка пароля
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Создание JWT токена
    token_data = {
        "sub": str(user.user_id),
        "login": user.login,
        "role_id": user.role_id
    }
    access_token = create_access_token(data=token_data)

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserAccountWithRole, summary="Получить текущего пользователя")
async def get_current_user_info(
    current_user: UserAccount = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserAccountWithRole:
    """
    Получение информации о текущем аутентифицированном пользователе

    Требует JWT токен в заголовке Authorization: Bearer <token>

    Возвращает полную информацию о пользователе включая роль

    Коды ошибок:
    - 401: Токен невалидный или пользователь не найден
    """
    # Загружаем связанную роль для получения role_name и role_shortname
    stmt = (
        select(UserAccount)
        .where(UserAccount.user_id == current_user.user_id)
        .options(selectinload(UserAccount.role))
    )
    result = await db.execute(stmt)
    user = result.scalar_one()

    # Формируем ответ с данными роли
    return UserAccountWithRole(
        user_id=user.user_id,
        login=user.login,
        email=user.email,
        last_name=user.last_name,
        first_name=user.first_name,
        patronymic=user.patronymic,
        registration_date=user.registration_date,
        role_id=user.role_id,
        role_name=user.role.role_name,
        role_shortname=user.role.role_shortname
    )
