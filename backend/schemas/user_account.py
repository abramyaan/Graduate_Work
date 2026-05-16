"""
Pydantic схемы для UserAccount (пользователи)
"""
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator
import re


class UserAccountBase(BaseModel):
    """Базовая схема пользователя"""
    login: str = Field(..., min_length=5, max_length=50, description="Логин")
    email: str = Field(..., max_length=100, description="Email")
    last_name: str = Field(..., min_length=1, max_length=100, description="Фамилия")
    first_name: str = Field(..., min_length=1, max_length=100, description="Имя")
    patronymic: Optional[str] = Field(None, max_length=100, description="Отчество")
    role_id: int = Field(..., gt=0, description="ID роли")


class UserAccountCreate(UserAccountBase):
    """Схема для создания пользователя"""
    password: str = Field(..., min_length=8, max_length=100,
                          description="Пароль (минимум 8 символов)")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Валидация пароля: минимум 8 символов, хотя бы одна цифра и буква"""
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        if not re.search(r'[A-Za-z]', v):
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        if not re.search(r'\d', v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v


class UserAccountUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    patronymic: Optional[str] = Field(None, max_length=100)
    role_id: Optional[int] = Field(None, gt=0)
    password: Optional[str] = Field(None, min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Валидация пароля если он передан"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        if not re.search(r'[A-Za-z]', v):
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        if not re.search(r'\d', v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v


class UserAccountResponse(UserAccountBase):
    """Схема ответа с данными пользователя (без пароля)"""
    user_id: int
    registration_date: date

    model_config = ConfigDict(from_attributes=True)


class UserAccountWithRole(UserAccountResponse):
    """Расширенная схема пользователя с данными роли"""
    role_name: Optional[str] = None
    role_shortname: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Схема для логина"""
    login: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)


class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные из JWT токена"""
    user_id: Optional[int] = None
    login: Optional[str] = None
