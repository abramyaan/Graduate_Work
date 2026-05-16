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


class ResultEvaluationDetailed(ResultEvaluationResponse):
    """Детальная схема результата оценки с доп. данными"""
    candidate_last_name: Optional[str] = None
    candidate_first_name: Optional[str] = None
    vacancy_title: Optional[str] = None
    recommendation_text: Optional[str] = None
    category_scores: List[ResultCategoryScoreResponse] = []
    user_login: Optional[str] = None
    model_name: Optional[str] = None

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
