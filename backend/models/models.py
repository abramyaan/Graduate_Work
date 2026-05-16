"""
ORM модели SQLAlchemy для всех 18 таблиц БД
SQLAlchemy 2.0 синхронный стиль
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    String, Integer, Text, Date, DateTime, Boolean, Numeric,
    ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.database import Base


# =============================================================================
# 1. UserRole — Роли пользователей (справочник)
# =============================================================================

class UserRole(Base):
    """Справочник ролей пользователей системы"""
    __tablename__ = "user_role"

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    role_shortname: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Связи
    users: Mapped[list["UserAccount"]] = relationship("UserAccount", back_populates="role")

    __table_args__ = (
        CheckConstraint("LENGTH(role_name) > 0", name="check_role_name"),
    )


# =============================================================================
# 2. UserAccount — Пользователи системы (сотрудники)
# =============================================================================

class UserAccount(Base):
    """Пользователи системы — сотрудники организации"""
    __tablename__ = "user_account"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    registration_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_role.role_id"), nullable=False)

    # Связи
    role: Mapped["UserRole"] = relationship("UserRole", back_populates="users")
    evaluations: Mapped[list["ResultEvaluation"]] = relationship("ResultEvaluation", back_populates="user")
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="user")

    __table_args__ = (
        CheckConstraint("LENGTH(login) >= 5", name="check_login_length"),
        CheckConstraint("LENGTH(password_hash) >= 60", name="check_password_hash"),
        CheckConstraint("email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name="check_email_format"),
        CheckConstraint("registration_date <= CURRENT_DATE", name="check_reg_date"),
        CheckConstraint("LENGTH(last_name) > 0", name="check_last_name"),
        CheckConstraint("LENGTH(first_name) > 0", name="check_first_name"),
    )


# =============================================================================
# 3. Candidate — Кандидаты (внешние лица)
# =============================================================================

class Candidate(Base):
    """Кандидаты — внешние лица, подающие резюме"""
    __tablename__ = "candidate"

    candidate_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Связи
    resumes: Mapped[list["Resume"]] = relationship("Resume", back_populates="candidate")

    __table_args__ = (
        CheckConstraint("LENGTH(last_name) > 0", name="check_cand_last_name"),
        CheckConstraint("LENGTH(first_name) > 0", name="check_cand_first_name"),
        CheckConstraint("email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
                       name="check_cand_email"),
        CheckConstraint("phone IS NULL OR phone ~ '^\\+?[0-9\\s\\-\\(\\)]{7,20}$'",
                       name="check_cand_phone"),
    )


# =============================================================================
# 4. Specialization — Специализации (справочник)
# =============================================================================

class Specialization(Base):
    """Справочник специализаций вакансий"""
    __tablename__ = "specialization"

    specialization_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)

    # Связи
    vacancies: Mapped[list["Vacancy"]] = relationship("Vacancy", back_populates="specialization")

    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="check_spec_name"),
    )


# =============================================================================
# 5. Vacancy — Вакансии
# =============================================================================

class Vacancy(Base):
    """Вакансии, на которые проводится оценка резюме"""
    __tablename__ = "vacancy"

    vacancy_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    specialization_id: Mapped[int] = mapped_column(Integer, ForeignKey("specialization.specialization_id"),
                                                     nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    # Связи
    specialization: Mapped["Specialization"] = relationship("Specialization", back_populates="vacancies")
    skills: Mapped[list["Skill"]] = relationship("Skill", secondary="vacancy_skill", back_populates="vacancies")
    resume_applications: Mapped[list["ResumeVacancy"]] = relationship("ResumeVacancy", back_populates="vacancy")
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="vacancy")

    __table_args__ = (
        CheckConstraint("LENGTH(title) >= 5", name="check_vacancy_title"),
        CheckConstraint("created_at <= CURRENT_DATE", name="check_vacancy_date"),
    )


# =============================================================================
# 6. Skill — Навыки (справочник)
# =============================================================================

class Skill(Base):
    """Справочник навыков (технологий, инструментов)"""
    __tablename__ = "skill"

    skill_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Связи
    vacancies: Mapped[list["Vacancy"]] = relationship("Vacancy", secondary="vacancy_skill", back_populates="skills")
    resumes: Mapped[list["Resume"]] = relationship("Resume", secondary="resume_skill", back_populates="skills")

    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="check_skill_name"),
    )


# =============================================================================
# 7. VacancySkill — Навыки вакансии (связующая M:M)
# =============================================================================

class VacancySkill(Base):
    """Навыки, требуемые вакансией"""
    __tablename__ = "vacancy_skill"

    vacancy_id: Mapped[int] = mapped_column(Integer, ForeignKey("vacancy.vacancy_id"),
                                             primary_key=True)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skill.skill_id"),
                                           primary_key=True)


# =============================================================================
# 8. Resume — Резюме кандидатов
# =============================================================================

class Resume(Base):
    """Загруженные резюме кандидатов"""
    __tablename__ = "resume"

    resume_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    file_format: Mapped[str] = mapped_column(String(10), nullable=False)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    upload_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidate.candidate_id"),
                                                nullable=False, index=True)

    # Связи
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="resumes")
    skills: Mapped[list["Skill"]] = relationship("Skill", secondary="resume_skill", back_populates="resumes")
    vacancy_applications: Mapped[list["ResumeVacancy"]] = relationship("ResumeVacancy", back_populates="resume")
    evaluations: Mapped[list["ResultEvaluation"]] = relationship("ResultEvaluation", back_populates="resume")

    __table_args__ = (
        CheckConstraint("file_format IN ('pdf', 'docx')", name="check_file_format"),
        CheckConstraint("upload_date <= CURRENT_DATE", name="check_upload_date"),
        CheckConstraint("LENGTH(file_path) > 0", name="check_file_path"),
    )


# =============================================================================
# 9. ResumeVacancy — Подача резюме на вакансию (связующая M:M)
# =============================================================================

class ResumeVacancy(Base):
    """Факт подачи резюме на конкретную вакансию"""
    __tablename__ = "resume_vacancy"

    resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resume.resume_id"),
                                            primary_key=True)
    vacancy_id: Mapped[int] = mapped_column(Integer, ForeignKey("vacancy.vacancy_id"),
                                             primary_key=True, index=True)
    applied_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    # Связи
    resume: Mapped["Resume"] = relationship("Resume", back_populates="vacancy_applications")
    vacancy: Mapped["Vacancy"] = relationship("Vacancy", back_populates="resume_applications")

    __table_args__ = (
        CheckConstraint("applied_at <= CURRENT_DATE", name="check_applied_date"),
    )


# =============================================================================
# 10. ResumeSkill — Навыки резюме (связующая M:M)
# =============================================================================

class ResumeSkill(Base):
    """Навыки, указанные в резюме кандидата"""
    __tablename__ = "resume_skill"

    resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resume.resume_id"),
                                            primary_key=True)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skill.skill_id"),
                                           primary_key=True)


# =============================================================================
# 11. EvaluationCategory — Категории оценки
# =============================================================================

class EvaluationCategory(Base):
    """Категории оценки соответствия резюме вакансии"""
    __tablename__ = "evaluation_category"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    weight: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)

    # Связи
    scores: Mapped[list["ResultCategoryScore"]] = relationship("ResultCategoryScore", back_populates="category")

    __table_args__ = (
        CheckConstraint("weight >= 0 AND weight <= 1", name="check_weight"),
    )


# =============================================================================
# 12. Model — ML-модели
# =============================================================================

class Model(Base):
    """ML-модели sentence-transformers для оценки соответствия"""
    __tablename__ = "model"

    model_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    artifact_path: Mapped[str] = mapped_column(String(255), nullable=False)
    finetune_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    # Связи
    configs: Mapped[list["ModelConfig"]] = relationship("ModelConfig", back_populates="model")
    evaluations: Mapped[list["ResultEvaluation"]] = relationship("ResultEvaluation", back_populates="model")
    training_pairs: Mapped[list["TrainingPair"]] = relationship("TrainingPair", back_populates="model")

    __table_args__ = (
        CheckConstraint("finetune_date <= CURRENT_DATE", name="check_finetune_date"),
        CheckConstraint("LENGTH(artifact_path) > 0", name="check_artifact_path"),
    )


# =============================================================================
# 13. ModelConfig — Параметры модели
# =============================================================================

class ModelConfig(Base):
    """Гиперпараметры дообучения ML-модели"""
    __tablename__ = "model_config"

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("model.model_id"), nullable=False)
    param_name: Mapped[str] = mapped_column(String(100), nullable=False)
    param_value: Mapped[str] = mapped_column(String(255), nullable=False)

    # Связи
    model: Mapped["Model"] = relationship("Model", back_populates="configs")

    __table_args__ = (
        UniqueConstraint("model_id", "param_name", name="uq_model_param"),
        CheckConstraint("LENGTH(param_name) > 0", name="check_param_name"),
    )


# =============================================================================
# 14. RecommendationRule — Правила рекомендаций
# =============================================================================

class RecommendationRule(Base):
    """Пороговые правила для автоматических рекомендаций"""
    __tablename__ = "recommendation_rule"

    recommendation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    min_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    max_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    recommendation_text: Mapped[str] = mapped_column(String(100), nullable=False)

    # Связи
    evaluations: Mapped[list["ResultEvaluation"]] = relationship("ResultEvaluation",
                                                                  back_populates="recommendation")

    __table_args__ = (
        CheckConstraint("min_score >= 0 AND max_score <= 100", name="check_score_range"),
        CheckConstraint("max_score > min_score", name="check_score_order"),
        CheckConstraint("LENGTH(recommendation_text) > 0", name="check_rec_text"),
    )


# =============================================================================
# 15. ResultEvaluation — Результаты оценки
# =============================================================================

class ResultEvaluation(Base):
    """Результаты оценки резюме на соответствие вакансии"""
    __tablename__ = "result_evaluation"

    result_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    overall_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    analysis_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now,
                                                      index=True)
    resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resume.resume_id"),
                                            nullable=False, index=True)
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("model.model_id"),
                                           nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.user_id"),
                                          nullable=False, index=True)
    recommendation_id: Mapped[int] = mapped_column(Integer,
                                                     ForeignKey("recommendation_rule.recommendation_id"),
                                                     nullable=False)

    # Связи
    resume: Mapped["Resume"] = relationship("Resume", back_populates="evaluations")
    model: Mapped["Model"] = relationship("Model", back_populates="evaluations")
    user: Mapped["UserAccount"] = relationship("UserAccount", back_populates="evaluations")
    recommendation: Mapped["RecommendationRule"] = relationship("RecommendationRule",
                                                                 back_populates="evaluations")
    category_scores: Mapped[list["ResultCategoryScore"]] = relationship("ResultCategoryScore",
                                                                          back_populates="result")

    __table_args__ = (
        CheckConstraint("overall_score >= 0 AND overall_score <= 100", name="check_overall_score"),
        CheckConstraint("analysis_date <= CURRENT_TIMESTAMP", name="check_analysis_date"),
    )


# =============================================================================
# 16. ResultCategoryScore — Детализация оценок по категориям
# =============================================================================

class ResultCategoryScore(Base):
    """Детальные оценки по каждой категории для результата"""
    __tablename__ = "result_category_score"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    result_id: Mapped[int] = mapped_column(Integer, ForeignKey("result_evaluation.result_id"),
                                            nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_category.category_id"),
                                              nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    # Связи
    result: Mapped["ResultEvaluation"] = relationship("ResultEvaluation", back_populates="category_scores")
    category: Mapped["EvaluationCategory"] = relationship("EvaluationCategory", back_populates="scores")

    __table_args__ = (
        UniqueConstraint("result_id", "category_id", name="uq_result_category"),
        CheckConstraint("score >= 0 AND score <= 100", name="check_category_score"),
    )


# =============================================================================
# 17. TrainingPair — Датасет для дообучения
# =============================================================================

class TrainingPair(Base):
    """Датасет пар резюме-вакансия для дообучения модели"""
    __tablename__ = "training_pair"

    pair_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_text: Mapped[str] = mapped_column(Text, nullable=False)
    vacancy_text: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    created_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    model_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("model.model_id"),
                                                      nullable=True)

    # Связи
    model: Mapped[Optional["Model"]] = relationship("Model", back_populates="training_pairs")

    __table_args__ = (
        CheckConstraint("label >= 0 AND label <= 1", name="check_label"),
        CheckConstraint("created_at <= CURRENT_DATE", name="check_pair_date"),
        CheckConstraint("LENGTH(resume_text) > 0", name="check_resume_txt"),
        CheckConstraint("LENGTH(vacancy_text) > 0", name="check_vacancy_txt"),
    )


# =============================================================================
# 18. Report — История отчётов
# =============================================================================

class Report(Base):
    """История сформированных отчётов"""
    __tablename__ = "report"

    report_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    file_format: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.user_id"), nullable=False)
    vacancy_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("vacancy.vacancy_id"),
                                                        nullable=True)
    candidate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Связи
    user: Mapped["UserAccount"] = relationship("UserAccount", back_populates="reports")
    vacancy: Mapped[Optional["Vacancy"]] = relationship("Vacancy", back_populates="reports")

    __table_args__ = (
        CheckConstraint("file_format IN ('pdf', 'xlsx')", name="check_report_format"),
        CheckConstraint("created_at <= CURRENT_TIMESTAMP", name="check_report_date"),
        CheckConstraint("candidate_count >= 0", name="check_cand_count"),
        CheckConstraint("LENGTH(file_path) > 0", name="check_report_path"),
    )
