"""
Экспорт всех ORM моделей
"""
from backend.models.models import (
    UserRole,
    UserAccount,
    Candidate,
    Specialization,
    Vacancy,
    Skill,
    VacancySkill,
    Resume,
    ResumeVacancy,
    ResumeSkill,
    EvaluationCategory,
    Model,
    ModelConfig,
    RecommendationRule,
    ResultEvaluation,
    ResultCategoryScore,
    TrainingPair,
    Report,
)

__all__ = [
    "UserRole",
    "UserAccount",
    "Candidate",
    "Specialization",
    "Vacancy",
    "Skill",
    "VacancySkill",
    "Resume",
    "ResumeVacancy",
    "ResumeSkill",
    "EvaluationCategory",
    "Model",
    "ModelConfig",
    "RecommendationRule",
    "ResultEvaluation",
    "ResultCategoryScore",
    "TrainingPair",
    "Report",
]
