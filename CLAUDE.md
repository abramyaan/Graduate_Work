# Проект: ПИС «Интеллектуальная оценка резюме на соответствие вакансии»

## Стек
- Backend: Python 3.11+, FastAPI, SQLAlchemy, Pydantic v2
- ML: sentence-transformers, torch, scikit-learn
- Frontend: React 18, TypeScript, Vite, Axios
- БД: PostgreSQL 14+
- Контейнеризация: Docker, docker-compose
- Инструменты: black, ruff, pytest

## Структура проекта
```
GraduateWork/
├── backend/
│   ├── main.py               # точка входа FastAPI
│   ├── api/                  # роутеры (routes)
│   ├── core/                 # config, security, dependencies
│   ├── models/               # SQLAlchemy ORM модели
│   ├── schemas/              # Pydantic схемы запросов/ответов
│   ├── services/             # бизнес-логика
│   └── db/                   # сессия БД, база
├── ml/
│   ├── train.py              # fine-tuning sentence-transformers
│   ├── evaluate.py           # расчёт соответствия резюме и вакансии
│   └── models/               # артефакты обученных моделей (.pt)
├── frontend/
│   ├── src/
│   │   ├── pages/            # страницы (Login, Dashboard, Results)
│   │   ├── components/       # компоненты React
│   │   ├── api/              # axios клиент
│   │   └── types/            # TypeScript типы
│   └── vite.config.ts
├── db/
│   └── schema.sql            # CREATE TABLE скрипты из DATABASE_SCHEMA.md
├── dataset/
│   └── dataset_training.json # датасет для fine-tuning
├── .env                      # переменные окружения (не коммитить)
├── docker-compose.yml
├── DATABASE_SCHEMA.md        # полная схема БД — читать перед любой работой с БД
└── CONTEXT.md                # контекст проекта
```

## Команды
```bash
# Backend
uvicorn backend.main:app --reload

# БД
docker-compose up -d postgres

# Fine-tuning модели
python ml/train.py

# Frontend
cd frontend && npm run dev

# Тесты
pytest backend/tests/
```

## Переменные окружения (.env)
```
DATABASE_URL=postgresql+pg8000://user:pass@localhost:5432/resume_db
MODEL_PATH=ml/models/finetuned_model
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Соглашения по коду
- Язык: Python 3.11+, TypeScript строгий режим
- Форматтер Python: black
- Линтер Python: ruff
- Типизация: обязательна везде — typing в Python, TypeScript на фронте
- Все строки интерфейса и комментарии в коде на русском языке
- Pydantic v2 для всех схем (не v1)
- SQLAlchemy 2.0 async стиль
- Роутеры FastAPI разбиты по сущностям (один файл — один роутер)

## Важные бизнес-правила
- Метка соответствия в датасете: float 0.0–1.0
- В БД overall_score хранится как NUMERIC(5,2) от 0.00 до 100.00
- Базовая модель: sentence-transformers/paraphrase-multilingual-mpnet-base-v2
- Веса категорий оценки: навыки 40%, опыт 30%, структура 20%, ATS 10%
- Рекомендация определяется через таблицу recommendation_rule — не хардкодить в коде
- recommendation_rule: >= 75 → «Пригласить немедленно», 50–74 → «Отложить», < 50 → «Отклонить»
- Файлы резюме: только .pdf и .docx, хранить в files/resumes/
- Артефакты модели хранить в files/models/

## Перед любой работой с БД
Обязательно прочитай файл DATABASE_SCHEMA.md — там полная схема с 18 таблицами,
порядком создания, FK-зависимостями, триггерами и матрицей доступа.

## Роли пользователей
- Администратор (Admin): полный доступ RIUD ко всем таблицам
- Рекрутер (Recruiter): только чтение результатов и отчётов
- Оператор (Operator): загрузка данных, запуск оценки, просмотр результатов
