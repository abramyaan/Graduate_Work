"""
Pydantic схемы для Candidate (кандидаты)
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
import re


class CandidateBase(BaseModel):
    """Базовая схема кандидата"""
    last_name: str = Field(..., min_length=1, max_length=100, description="Фамилия")
    first_name: str = Field(..., min_length=1, max_length=100, description="Имя")
    patronymic: Optional[str] = Field(None, max_length=100, description="Отчество")
    email: Optional[EmailStr] = Field(None, description="Email кандидата")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Валидация формата телефона"""
        if v is None:
            return v
        # Регулярное выражение для телефона: +79161234567, 8 (916) 123-45-67 и т.д.
        if not re.match(r'^\+?[0-9\s\-\(\)]{7,20}$', v):
            raise ValueError("Неверный формат телефона")
        return v


class CandidateCreate(CandidateBase):
    """Схема для создания кандидата"""
    pass


class CandidateUpdate(BaseModel):
    """Схема для обновления кандидата"""
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    patronymic: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Валидация формата телефона"""
        if v is None:
            return v
        if not re.match(r'^\+?[0-9\s\-\(\)]{7,20}$', v):
            raise ValueError("Неверный формат телефона")
        return v


class CandidateResponse(CandidateBase):
    """Схема ответа с данными кандидата"""
    candidate_id: int

    model_config = ConfigDict(from_attributes=True)


class CandidateWithResumes(CandidateResponse):
    """Расширенная схема кандидата с количеством резюме"""
    resume_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
