"""
Pydantic схемы для ResultEvaluation (результаты оценки)
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class ResultCategoryScoreBase(BaseModel):
    """Базовая схема оценки по категории"""
    category_id: int = Field(..., gt=0)
    score: Decimal = Field(..., ge=0, le=100, decimal_places=2)


class ResultCategoryScoreCreate(ResultCategoryScoreBase):
    """Схема для создания оценки по категории"""
    pass


class ResultCategoryScoreResponse(ResultCategoryScoreBase):
    """Схема ответа оценки по категории"""
    id: int
    result_id: int
    category_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ResultEvaluationBase(BaseModel):
    """Базовая схема результата оценки"""
    overall_score: Decimal = Field(..., ge=0, le=100, decimal_places=2,
                                    description="Общий балл 0.00-100.00")
    resume_id: int = Field(..., gt=0, description="ID резюме")
    model_id: int = Field(..., gt=0, description="ID модели")
    user_id: int = Field(..., gt=0, description="ID пользователя")
    recommendation_id: int = Field(..., gt=0, description="ID рекомендации")


class ResultEvaluationCreate(BaseModel):
    """Схема для создания результата оценки"""
    resume_id: int = Field(..., gt=0)
    model_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    overall_score: Decimal = Field(..., ge=0, le=100, decimal_places=2)
    category_scores: List[ResultCategoryScoreCreate] = Field(
        ...,
        description="Оценки по категориям"
    )

    # recommendation_id вычисляется автоматически на основе overall_score


class ResultEvaluationUpdate(BaseModel):
    """Схема для обновления результата оценки"""
    overall_score: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    recommendation_id: Optional[int] = Field(None, gt=0)


class ResultEvaluationResponse(ResultEvaluationBase):
    """Схема ответа с данными результата"""
    result_id: int
    analysis_date: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateInfo(BaseModel):
    """Информация о кандидате"""
    candidate_id: int
    last_name: str
    first_name: str
    patronymic: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class VacancyInfo(BaseModel):
    """Информация о вакансии"""
    vacancy_id: int
    title: str
    description: Optional[str] = None
    specialization_id: Optional[int] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class CategoryScoreDetailed(BaseModel):
    """Детальная оценка по категории"""
    category_name: str
    score: Decimal = Field(..., ge=0, le=100)
    weight: Decimal = Field(..., ge=0, le=1)
    weighted_score: Decimal = Field(..., ge=0, le=100)

    model_config = ConfigDict(from_attributes=True)


class ResultEvaluationDetailed(BaseModel):
    """Детальная схема результата оценки с доп. данными"""
    id: int
    candidate: CandidateInfo
    vacancy: VacancyInfo
    overall_score: Decimal = Field(..., ge=0, le=100)
    category_scores: List[CategoryScoreDetailed] = []
    recommendation: str
    evaluated_at: datetime
    evaluator_name: str
    resume_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ResultEvaluationListItem(BaseModel):
    """Схема элемента списка результатов (сокращённая)"""
    result_id: int
    overall_score: Decimal
    analysis_date: datetime
    candidate_name: str
    vacancy_title: Optional[str] = None
    recommendation_text: str

    model_config = ConfigDict(from_attributes=True)
