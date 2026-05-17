"""
Точка входа FastAPI приложения
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context для загрузки/выгрузки ресурсов при старте/остановке

    Загружает ML модель при старте сервера (занимает ~30 секунд)
    """
    print("\n" + "=" * 80)
    print("🚀 Запуск сервера - загрузка ML модели...")
    print("=" * 80)

    try:
        from ml.evaluate import ResumeEvaluator
        from backend.core.config import settings

        print(f"📁 Путь к модели: {settings.MODEL_PATH}")
        print("⏳ Загрузка займет 10-30 секунд, ожидайте...")

        app.state.evaluator = ResumeEvaluator(settings.MODEL_PATH)

        print("=" * 80)
        print("✅ ML модель успешно загружена и готова к использованию")
        print("=" * 80 + "\n")

    except FileNotFoundError as e:
        print("=" * 80)
        print(f"⚠️  ВНИМАНИЕ: Модель не найдена: {e}")
        print("   Эндпоинт /api/results/evaluate будет недоступен")
        print("   Запустите ml/train.py для обучения модели")
        print("=" * 80 + "\n")
        app.state.evaluator = None

    except ImportError as e:
        print("=" * 80)
        print(f"⚠️  ВНИМАНИЕ: Ошибка импорта библиотек: {e}")
        print("   Установите зависимости: pip install torch sentence-transformers")
        print("=" * 80 + "\n")
        app.state.evaluator = None

    except Exception as e:
        print("=" * 80)
        print(f"⚠️  ВНИМАНИЕ: Ошибка загрузки модели: {e}")
        print("   Эндпоинт /api/results/evaluate будет недоступен")
        print("=" * 80 + "\n")
        import traceback
        traceback.print_exc()
        app.state.evaluator = None

    yield

    # Очистка при остановке
    print("\n🛑 Остановка сервера...")
    app.state.evaluator = None


app = FastAPI(
    title="ПИС Интеллектуальная оценка резюме",
    description="API для автоматизации первичного скрининга кандидатов",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники (для разработки)
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
from backend.api import auth, vacancy, candidate, resume, result_evaluation, specialization, statistics

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

app.include_router(
    specialization.router,
    prefix="/api/specializations",
    tags=["Специализации"]
)

app.include_router(
    statistics.router,
    prefix="/api/statistics",
    tags=["Статистика"]
)
