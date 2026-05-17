"""
Роутер для работы с резюме
"""
from typing import List
import traceback
import PyPDF2
from docx import Document

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import os
from datetime import datetime

from backend.db.database import get_db
from backend.models.models import Resume, Candidate, Vacancy, ResumeVacancy
from backend.schemas.resume import (
    ResumeCreate,
    ResumeUpdate,
    ResumeResponse,
    ResumeWithCandidate,
    ResumeUploadResponse,
)
from backend.core.config import settings

router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    candidate_id: int = Form(...),
    vacancy_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Загрузить файл резюме (PDF или DOCX)
    Параметры передаются через multipart/form-data:
    - candidate_id: ID кандидата
    - vacancy_id: ID вакансии
    - file: Файл резюме (PDF или DOCX)
    """
    try:
        # Проверка формата файла
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя файла не указано"
            )

        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["pdf", "docx"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Разрешены только файлы PDF и DOCX"
            )

        # Проверка существования кандидата
        candidate = await db.get(Candidate, candidate_id)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Кандидат с ID {candidate_id} не найден"
            )

        # Проверка существования вакансии
        vacancy = await db.get(Vacancy, vacancy_id)
        if not vacancy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Вакансия с ID {vacancy_id} не найдена"
            )

        # Генерация уникального имени файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"resume_{candidate_id}_{timestamp}.{file_extension}"
        file_path = os.path.join(settings.FILES_RESUMES_PATH, safe_filename)

        # Сохранение файла
        os.makedirs(settings.FILES_RESUMES_PATH, exist_ok=True)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Парсинг текста из файла
        extracted_text = None
        try:
            if file_extension == "pdf":
                # Парсинг PDF с помощью PyPDF2
                with open(file_path, "rb") as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    extracted_text = " ".join(
                        page.extract_text() for page in reader.pages if page.extract_text()
                    )
            elif file_extension == "docx":
                # Парсинг DOCX с помощью python-docx
                doc = Document(file_path)
                extracted_text = " ".join(para.text for para in doc.paragraphs if para.text)
        except Exception as parse_error:
            # Логируем ошибку парсинга, но не прерываем загрузку файла
            print(f"⚠️  Ошибка парсинга файла {file_path}: {parse_error}")
            extracted_text = None

        # Создание записи Resume в БД
        resume = Resume(
            file_path=file_path,
            file_format=file_extension,
            candidate_id=candidate_id,
            extracted_text=extracted_text
        )
        db.add(resume)
        await db.commit()
        await db.refresh(resume)

        # Создание связи резюме с вакансией в ResumeVacancy
        resume_vacancy = ResumeVacancy(
            resume_id=resume.resume_id,
            vacancy_id=vacancy_id
        )
        db.add(resume_vacancy)
        await db.commit()

        return ResumeUploadResponse(
            resume_id=resume.resume_id,
            file_path=resume.file_path,
            file_format=resume.file_format,
            message="Резюме успешно загружено"
        )
    except Exception as e:
        # Детальное логирование ошибки
        error_detail = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "received_params": {
                "candidate_id": candidate_id if 'candidate_id' in locals() else "NOT_RECEIVED",
                "vacancy_id": vacancy_id if 'vacancy_id' in locals() else "NOT_RECEIVED",
                "file": file.filename if 'file' in locals() and file else "NOT_RECEIVED"
            }
        }
        print("=== ERROR IN upload_resume ===")
        print(error_detail)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.post("/", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    resume_data: ResumeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать резюме (без загрузки файла - для тестирования)"""
    # Проверка существования кандидата
    candidate = await db.get(Candidate, resume_data.candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кандидат с ID {resume_data.candidate_id} не найден"
        )

    # Генерация пути к файлу
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"files/resumes/resume_{resume_data.candidate_id}_{timestamp}.{resume_data.file_format}"

    resume = Resume(
        file_path=file_path,
        file_format=resume_data.file_format,
        candidate_id=resume_data.candidate_id,
        extracted_text=resume_data.extracted_text
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return resume


@router.get("/", response_model=List[ResumeWithCandidate])
async def get_resumes(
    skip: int = 0,
    limit: int = 100,
    candidate_id: int = None,
    vacancy_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех резюме с фильтрацией по candidate_id или vacancy_id"""
    query = select(Resume).options(selectinload(Resume.candidate)).join(Candidate)

    if candidate_id is not None:
        query = query.where(Resume.candidate_id == candidate_id)

    if vacancy_id is not None:
        # Фильтрация по vacancy_id через ResumeVacancy
        query = query.join(ResumeVacancy).where(ResumeVacancy.vacancy_id == vacancy_id)

    query = query.offset(skip).limit(limit)
    result_query = await db.execute(query)
    resumes = result_query.scalars().all()

    # Формирование ответа с данными кандидата из уже загруженного relationship
    result = []
    for resume in resumes:
        result.append(
            ResumeWithCandidate(
                resume_id=resume.resume_id,
                file_path=resume.file_path,
                file_format=resume.file_format,
                extracted_text=resume.extracted_text,
                upload_date=resume.upload_date,
                candidate_id=resume.candidate_id,
                candidate_last_name=resume.candidate.last_name,
                candidate_first_name=resume.candidate.first_name,
                candidate_patronymic=resume.candidate.patronymic,
            )
        )

    return result


@router.get("/{resume_id}", response_model=ResumeWithCandidate)
async def get_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить резюме по ID"""
    query = select(Resume).options(selectinload(Resume.candidate)).where(Resume.resume_id == resume_id)
    result = await db.execute(query)
    resume = result.scalar_one_or_none()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Резюме с ID {resume_id} не найдено"
        )

    return ResumeWithCandidate(
        resume_id=resume.resume_id,
        file_path=resume.file_path,
        file_format=resume.file_format,
        extracted_text=resume.extracted_text,
        upload_date=resume.upload_date,
        candidate_id=resume.candidate_id,
        candidate_last_name=resume.candidate.last_name,
        candidate_first_name=resume.candidate.first_name,
        candidate_patronymic=resume.candidate.patronymic,
    )


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: int,
    resume_data: ResumeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить резюме (только extracted_text)"""
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Резюме с ID {resume_id} не найдено"
        )

    # Обновление полей
    update_data = resume_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resume, field, value)

    await db.commit()
    await db.refresh(resume)

    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить резюме"""
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Резюме с ID {resume_id} не найдено"
        )

    # Удаление физического файла если он существует
    if os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception as e:
            # Логируем ошибку но не прерываем удаление из БД
            print(f"Ошибка при удалении файла {resume.file_path}: {e}")

    db.delete(resume)
    await db.commit()

    return None
