"""
Экспорт всех Pydantic схем
"""
from backend.schemas.vacancy import (
    VacancyBase,
    VacancyCreate,
    VacancyUpdate,
    VacancyResponse,
    VacancyWithSpecialization,
)
from backend.schemas.candidate import (
    CandidateBase,
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateWithResumes,
)
from backend.schemas.resume import (
    ResumeBase,
    ResumeCreate,
    ResumeUpdate,
    ResumeResponse,
    ResumeWithCandidate,
    ResumeUploadResponse,
)
from backend.schemas.result_evaluation import (
    ResultEvaluationBase,
    ResultEvaluationCreate,
    ResultEvaluationUpdate,
    ResultEvaluationResponse,
    ResultEvaluationDetailed,
    ResultEvaluationListItem,
    ResultCategoryScoreBase,
    ResultCategoryScoreCreate,
    ResultCategoryScoreResponse,
)
from backend.schemas.user_account import (
    UserAccountBase,
    UserAccountCreate,
    UserAccountUpdate,
    UserAccountResponse,
    UserAccountWithRole,
    UserLogin,
    Token,
    TokenData,
)

__all__ = [
    # Vacancy
    "VacancyBase",
    "VacancyCreate",
    "VacancyUpdate",
    "VacancyResponse",
    "VacancyWithSpecialization",
    # Candidate
    "CandidateBase",
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateResponse",
    "CandidateWithResumes",
    # Resume
    "ResumeBase",
    "ResumeCreate",
    "ResumeUpdate",
    "ResumeResponse",
    "ResumeWithCandidate",
    "ResumeUploadResponse",
    # Result Evaluation
    "ResultEvaluationBase",
    "ResultEvaluationCreate",
    "ResultEvaluationUpdate",
    "ResultEvaluationResponse",
    "ResultEvaluationDetailed",
    "ResultEvaluationListItem",
    "ResultCategoryScoreBase",
    "ResultCategoryScoreCreate",
    "ResultCategoryScoreResponse",
    # User Account
    "UserAccountBase",
    "UserAccountCreate",
    "UserAccountUpdate",
    "UserAccountResponse",
    "UserAccountWithRole",
    "UserLogin",
    "Token",
    "TokenData",
]
