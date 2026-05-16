"""
Роутер для работы с результатами оценки
"""
from typing import List
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from backend.db.database import get_db
from backend.models.models import (
    ResultEvaluation,
    ResultCategoryScore,
    Resume,
    Model,
    UserAccount,
    RecommendationRule,
    EvaluationCategory,
    Candidate,
    ResumeVacancy,
    Vacancy,
)
from backend.schemas.result_evaluation import (
    ResultEvaluationCreate,
    ResultEvaluationUpdate,
    ResultEvaluationResponse,
    ResultEvaluationDetailed,
    ResultEvaluationListItem,
)

router = APIRouter()


def determine_recommendation(overall_score: Decimal, db: Session) -> int:
    """Определить recommendation_id на основе overall_score"""
    rules = db.execute(select(RecommendationRule)).scalars().all()

    for rule in rules:
        if rule.min_score <= overall_score <= rule.max_score:
            return rule.recommendation_id

    # По умолчанию - самая низкая рекомендация
    lowest_rule = min(rules, key=lambda r: r.min_score)
    return lowest_rule.recommendation_id


@router.post("/", response_model=ResultEvaluationResponse, status_code=status.HTTP_201_CREATED)
def create_evaluation(
    evaluation_data: ResultEvaluationCreate,
    db: Session = Depends(get_db)
):
    """Создать результат оценки резюме"""
    # Проверка существования связанных сущностей
    resume = db.get(Resume, evaluation_data.resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Резюме с ID {evaluation_data.resume_id} не найдено"
        )

    model = db.get(Model, evaluation_data.model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модель с ID {evaluation_data.model_id} не найдена"
        )

    user = db.get(UserAccount, evaluation_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {evaluation_data.user_id} не найден"
        )

    # Определение рекомендации на основе overall_score
    recommendation_id = determine_recommendation(evaluation_data.overall_score, db)

    # Создание результата оценки
    result = ResultEvaluation(
        overall_score=evaluation_data.overall_score,
        resume_id=evaluation_data.resume_id,
        model_id=evaluation_data.model_id,
        user_id=evaluation_data.user_id,
        recommendation_id=recommendation_id,
    )
    db.add(result)
    db.flush()  # Получаем result_id до commit

    # Создание оценок по категориям
    for category_score in evaluation_data.category_scores:
        # Проверка существования категории
        category = db.get(EvaluationCategory, category_score.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория с ID {category_score.category_id} не найдена"
            )

        score = ResultCategoryScore(
            result_id=result.result_id,
            category_id=category_score.category_id,
            score=category_score.score,
        )
        db.add(score)

    db.commit()
    db.refresh(result)

    return result


@router.get("/", response_model=List[ResultEvaluationListItem])
def get_evaluations(
    skip: int = 0,
    limit: int = 100,
    resume_id: int = None,
    db: Session = Depends(get_db)
):
    """Получить список всех результатов оценки"""
    query = (
        select(ResultEvaluation)
        .join(Resume)
        .join(Candidate)
        .join(RecommendationRule)
        .outerjoin(ResumeVacancy)
        .outerjoin(Vacancy)
    )

    if resume_id is not None:
        query = query.where(ResultEvaluation.resume_id == resume_id)

    query = query.order_by(desc(ResultEvaluation.overall_score)).offset(skip).limit(limit)
    results = db.execute(query).scalars().all()

    # Формирование списка
    evaluations = []
    for result in results:
        # Получение вакансии через resume_vacancy
        vacancy_title = None
        if result.resume.vacancy_applications:
            vacancy_title = result.resume.vacancy_applications[0].vacancy.title

        candidate = result.resume.candidate
        candidate_name = f"{candidate.last_name} {candidate.first_name}"
        if candidate.patronymic:
            candidate_name += f" {candidate.patronymic}"

        evaluations.append(
            ResultEvaluationListItem(
                result_id=result.result_id,
                overall_score=result.overall_score,
                analysis_date=result.analysis_date,
                candidate_name=candidate_name,
                vacancy_title=vacancy_title,
                recommendation_text=result.recommendation.recommendation_text,
            )
        )

    return evaluations


@router.get("/{result_id}", response_model=ResultEvaluationDetailed)
def get_evaluation(
    result_id: int,
    db: Session = Depends(get_db)
):
    """Получить детальный результат оценки по ID"""
    result = db.get(ResultEvaluation, result_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Результат оценки с ID {result_id} не найден"
        )

    # Получение оценок по категориям
    category_scores = db.execute(
        select(ResultCategoryScore)
        .join(EvaluationCategory)
        .where(ResultCategoryScore.result_id == result_id)
    ).scalars().all()

    # Получение вакансии
    vacancy_title = None
    if result.resume.vacancy_applications:
        vacancy_title = result.resume.vacancy_applications[0].vacancy.title

    # Формирование детального ответа
    candidate = result.resume.candidate
    evaluation_dict = ResultEvaluationDetailed.model_validate(result).model_dump()
    evaluation_dict.update({
        "candidate_last_name": candidate.last_name,
        "candidate_first_name": candidate.first_name,
        "vacancy_title": vacancy_title,
        "recommendation_text": result.recommendation.recommendation_text,
        "user_login": result.user.login,
        "model_name": result.model.name,
        "category_scores": [
            {
                "id": cs.id,
                "result_id": cs.result_id,
                "category_id": cs.category_id,
                "score": cs.score,
                "category_name": cs.category.name,
            }
            for cs in category_scores
        ],
    })

    return ResultEvaluationDetailed(**evaluation_dict)


@router.put("/{result_id}", response_model=ResultEvaluationResponse)
def update_evaluation(
    result_id: int,
    evaluation_data: ResultEvaluationUpdate,
    db: Session = Depends(get_db)
):
    """Обновить результат оценки"""
    result = db.get(ResultEvaluation, result_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Результат оценки с ID {result_id} не найден"
        )

    # Если обновляется overall_score, пересчитываем recommendation_id
    update_data = evaluation_data.model_dump(exclude_unset=True)

    if "overall_score" in update_data:
        recommendation_id = determine_recommendation(update_data["overall_score"], db)
        update_data["recommendation_id"] = recommendation_id

    # Обновление полей
    for field, value in update_data.items():
        setattr(result, field, value)

    db.commit()
    db.refresh(result)

    return result


@router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evaluation(
    result_id: int,
    db: Session = Depends(get_db)
):
    """Удалить результат оценки"""
    result = db.get(ResultEvaluation, result_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Результат оценки с ID {result_id} не найден"
        )

    # Удаление связанных оценок по категориям (CASCADE)
    db.execute(
        select(ResultCategoryScore).where(ResultCategoryScore.result_id == result_id)
    )

    db.delete(result)
    db.commit()

    return None
