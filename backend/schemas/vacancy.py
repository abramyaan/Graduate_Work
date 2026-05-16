"""
Pydantic схемы для Vacancy (вакансии)
"""
from datetime import date
from typing import Optional, Any

from pydantic import BaseModel, Field, ConfigDict, model_validator


class VacancyBase(BaseModel):
    """Базовая схема вакансии"""
    title: str = Field(..., min_length=5, max_length=255, description="Заголовок вакансии")
    description: str = Field(..., min_length=1, description="Полное описание требований")
    specialization_id: int = Field(..., gt=0, description="ID специализации")
    is_active: bool = Field(default=True, description="Признак активности")


class VacancyCreate(VacancyBase):
    """Схема для создания вакансии"""
    pass


class VacancyUpdate(BaseModel):
    """Схема для обновления вакансии"""
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    specialization_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None


class VacancyResponse(VacancyBase):
    """Схема ответа с данными вакансии"""
    vacancy_id: int
    created_at: date

    model_config = ConfigDict(from_attributes=True)


class VacancyWithSpecialization(VacancyResponse):
    """Расширенная схема вакансии с данными специализации"""
    specialization_name: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def extract_specialization_name(cls, data: Any) -> Any:
        """Автоматически извлекает название специализации из загруженного relationship"""
        if isinstance(data, dict):
            return data

        # Если это ORM объект с relationship specialization
        if hasattr(data, 'specialization') and data.specialization:
            # Создаем словарь с данными, включая specialization_name
            if not hasattr(data, 'specialization_name'):
                # Используем __dict__ для избежания дополнительного SQL запроса
                result = {key: getattr(data, key) for key in cls.model_fields.keys() if hasattr(data, key)}
                result['specialization_name'] = data.specialization.name
                return result

        return data

    model_config = ConfigDict(from_attributes=True)
