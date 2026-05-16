"""
Точка входа FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ПИС Интеллектуальная оценка резюме",
    description="API для автоматизации первичного скрининга кандидатов",
    version="0.1.0",
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "ПИС Интеллектуальная оценка резюме",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy"}


# Подключение роутеров
from backend.api import auth, vacancy, candidate, resume, result_evaluation

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Авторизация"]
)

app.include_router(
    vacancy.router,
    prefix="/api/vacancies",
    tags=["Вакансии"]
)

app.include_router(
    candidate.router,
    prefix="/api/candidates",
    tags=["Кандидаты"]
)

app.include_router(
    resume.router,
    prefix="/api/resumes",
    tags=["Резюме"]
)

app.include_router(
    result_evaluation.router,
    prefix="/api/results",
    tags=["Результаты оценки"]
)
