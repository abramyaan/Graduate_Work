"""
Роутер для статистики и аналитики
"""
from typing import Dict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel

from backend.db.database import get_db
from backend.models.models import (
    Vacancy,
    Resume,
    ResultEvaluation,
    Candidate,
    ResumeVacancy,
    RecommendationRule
)

router = APIRouter()


class DashboardStats(BaseModel):
    """Статистика для Dashboard"""
    total_vacancies: int
    active_vacancies: int
    total_candidates: int
    total_resumes: int
    total_evaluations: int
    avg_score: float
    high_score_count: int  # >= 75
    medium_score_count: int  # 50-74
    low_score_count: int  # < 50


class VacancyStatsItem(BaseModel):
    """Статистика по вакансии"""
    vacancy_id: int
    title: str
    resume_count: int
    avg_score: float
    top_candidate: str | None


class RecentEvaluationItem(BaseModel):
    """Последняя оценка"""
    result_id: int
    candidate_name: str
    vacancy_title: str
    overall_score: float
    recommendation: str
    analysis_date: datetime


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """
    Получить общую статистику для Dashboard
    """
    # Количество вакансий
    total_vacancies_query = await db.execute(select(func.count(Vacancy.vacancy_id)))
    total_vacancies = total_vacancies_query.scalar() or 0

    active_vacancies_query = await db.execute(
        select(func.count(Vacancy.vacancy_id)).where(Vacancy.is_active == True)
    )
    active_vacancies = active_vacancies_query.scalar() or 0

    # Количество кандидатов
    total_candidates_query = await db.execute(select(func.count(Candidate.candidate_id)))
    total_candidates = total_candidates_query.scalar() or 0

    # Количество резюме
    total_resumes_query = await db.execute(select(func.count(Resume.resume_id)))
    total_resumes = total_resumes_query.scalar() or 0

    # Количество оценок
    total_evaluations_query = await db.execute(select(func.count(ResultEvaluation.result_id)))
    total_evaluations = total_evaluations_query.scalar() or 0

    # Средний балл
    avg_score_query = await db.execute(select(func.avg(ResultEvaluation.overall_score)))
    avg_score = float(avg_score_query.scalar() or 0)

    # Распределение по баллам
    high_score_query = await db.execute(
        select(func.count(ResultEvaluation.result_id)).where(ResultEvaluation.overall_score >= 75)
    )
    high_score_count = high_score_query.scalar() or 0

    medium_score_query = await db.execute(
        select(func.count(ResultEvaluation.result_id)).where(
            ResultEvaluation.overall_score >= 50,
            ResultEvaluation.overall_score < 75
        )
    )
    medium_score_count = medium_score_query.scalar() or 0

    low_score_query = await db.execute(
        select(func.count(ResultEvaluation.result_id)).where(ResultEvaluation.overall_score < 50)
    )
    low_score_count = low_score_query.scalar() or 0

    return DashboardStats(
        total_vacancies=total_vacancies,
        active_vacancies=active_vacancies,
        total_candidates=total_candidates,
        total_resumes=total_resumes,
        total_evaluations=total_evaluations,
        avg_score=avg_score,
        high_score_count=high_score_count,
        medium_score_count=medium_score_count,
        low_score_count=low_score_count
    )


@router.get("/vacancies/top", response_model=list[VacancyStatsItem])
async def get_top_vacancies(
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить топ вакансий по количеству резюме и среднему баллу
    """
    # Сложный запрос с GROUP BY и JOIN
    query = (
        select(
            Vacancy.vacancy_id,
            Vacancy.title,
            func.count(Resume.resume_id).label('resume_count'),
            func.avg(ResultEvaluation.overall_score).label('avg_score')
        )
        .select_from(Vacancy)
        .outerjoin(ResumeVacancy, ResumeVacancy.vacancy_id == Vacancy.vacancy_id)
        .outerjoin(Resume, Resume.resume_id == ResumeVacancy.resume_id)
        .outerjoin(ResultEvaluation, ResultEvaluation.resume_id == Resume.resume_id)
        .where(Vacancy.is_active == True)
        .group_by(Vacancy.vacancy_id, Vacancy.title)
        .order_by(desc('resume_count'))
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    stats = []
    for row in rows:
        # Получить лучшего кандидата для этой вакансии
        top_candidate_query = (
            select(Candidate.last_name, Candidate.first_name)
            .select_from(ResultEvaluation)
            .join(Resume, Resume.resume_id == ResultEvaluation.resume_id)
            .join(Candidate, Candidate.candidate_id == Resume.candidate_id)
            .join(ResumeVacancy, ResumeVacancy.resume_id == Resume.resume_id)
            .where(ResumeVacancy.vacancy_id == row.vacancy_id)
            .order_by(desc(ResultEvaluation.overall_score))
            .limit(1)
        )
        top_candidate_result = await db.execute(top_candidate_query)
        top_candidate_row = top_candidate_result.first()

        top_candidate = None
        if top_candidate_row:
            top_candidate = f"{top_candidate_row.last_name} {top_candidate_row.first_name}"

        stats.append(VacancyStatsItem(
            vacancy_id=row.vacancy_id,
            title=row.title,
            resume_count=row.resume_count or 0,
            avg_score=float(row.avg_score or 0),
            top_candidate=top_candidate
        ))

    return stats


@router.get("/evaluations/recent", response_model=list[RecentEvaluationItem])
async def get_recent_evaluations(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить последние оценки
    """
    query = (
        select(ResultEvaluation)
        .join(Resume, Resume.resume_id == ResultEvaluation.resume_id)
        .join(Candidate, Candidate.candidate_id == Resume.candidate_id)
        .outerjoin(ResumeVacancy, ResumeVacancy.resume_id == Resume.resume_id)
        .outerjoin(Vacancy, Vacancy.vacancy_id == ResumeVacancy.vacancy_id)
        .join(RecommendationRule, RecommendationRule.recommendation_id == ResultEvaluation.recommendation_id)
        .order_by(desc(ResultEvaluation.analysis_date))
        .limit(limit)
    )

    result = await db.execute(query)
    evaluations = result.scalars().all()

    items = []
    for evaluation in evaluations:
        # Загрузить связанные данные
        await db.refresh(evaluation, ['resume', 'recommendation'])
        await db.refresh(evaluation.resume, ['candidate', 'vacancy_applications'])

        candidate = evaluation.resume.candidate
        candidate_name = f"{candidate.last_name} {candidate.first_name}"
        if candidate.patronymic:
            candidate_name += f" {candidate.patronymic}"

        vacancy_title = "Не указана"
        if evaluation.resume.vacancy_applications:
            vacancy_app = evaluation.resume.vacancy_applications[0]
            await db.refresh(vacancy_app, ['vacancy'])
            vacancy_title = vacancy_app.vacancy.title

        items.append(RecentEvaluationItem(
            result_id=evaluation.result_id,
            candidate_name=candidate_name,
            vacancy_title=vacancy_title,
            overall_score=float(evaluation.overall_score),
            recommendation=evaluation.recommendation.recommendation_text,
            analysis_date=evaluation.analysis_date
        ))

    return items
