# ПИС «Интеллектуальная оценка резюме на соответствие вакансии»

Программная информационная система для автоматизации первичного скрининга кандидатов на основе семантического анализа резюме с использованием дообученных моделей sentence-transformers.

## Стек технологий

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **ML**: sentence-transformers, PyTorch, scikit-learn
- **Frontend**: React 18, TypeScript, Vite, Axios
- **БД**: PostgreSQL 14+
- **Контейнеризация**: Docker, docker-compose

## Структура проекта

```
GraduateWork/
├── backend/          # Backend на FastAPI
│   ├── api/          # Роутеры API
│   ├── core/         # Конфигурация, безопасность
│   ├── models/       # SQLAlchemy ORM модели
│   ├── schemas/      # Pydantic схемы
│   ├── services/     # Бизнес-логика
│   └── db/           # Подключение к БД
├── ml/               # ML-модуль
│   ├── train.py      # Fine-tuning модели
│   ├── evaluate.py   # Оценка соответствия
│   └── models/       # Артефакты моделей
├── frontend/         # Frontend на React + TypeScript
│   └── src/
├── db/               # SQL-скрипты
│   └── schema.sql    # Полная схема БД (18 таблиц)
├── dataset/          # Датасеты для обучения
└── files/            # Файловое хранилище
    ├── resumes/      # PDF/DOCX резюме
    ├── models/       # Веса моделей
    └── reports/      # Отчёты PDF/Excel
```

## Быстрый старт

### 1. Клонирование и настройка окружения

```bash
git clone <repository-url>
cd GraduateWork

# Создание виртуального окружения Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей Python (будет добавлено позже)
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env и установите свои значения
```

### 2. Запуск PostgreSQL

```bash
# Запуск БД через Docker Compose
docker-compose up -d postgres

# Проверка, что БД запущена
docker-compose ps

# Схема БД создастся автоматически при первом запуске
# (через docker-entrypoint-initdb.d/01_schema.sql)
```

### 3. Запуск Backend

```bash
# Из корня проекта
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# API будет доступно на http://localhost:8000
# Документация Swagger: http://localhost:8000/docs
```

### 4. Запуск Frontend

```bash
cd frontend
npm install
npm run dev

# Frontend будет доступен на http://localhost:5173
```

## База данных

Схема содержит **18 таблиц** в третьей нормальной форме (3НФ):

1. `user_role` — Роли пользователей
2. `user_account` — Пользователи системы
3. `candidate` — Кандидаты
4. `specialization` — Специализации (справочник)
5. `vacancy` — Вакансии
6. `skill` — Навыки (справочник)
7. `vacancy_skill` — Связь вакансий и навыков
8. `resume` — Резюме
9. `resume_vacancy` — Связь резюме и вакансий
10. `resume_skill` — Связь резюме и навыков
11. `evaluation_category` — Категории оценки
12. `model` — ML-модели
13. `model_config` — Параметры моделей
14. `recommendation_rule` — Правила рекомендаций
15. `result_evaluation` — Результаты оценки
16. `result_category_score` — Детализация по категориям
17. `training_pair` — Датасет для дообучения
18. `report` — История отчётов

Подробная документация: [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)

## Роли пользователей

- **Администратор (Admin)**: полный доступ ко всем таблицам (CRUD)
- **Рекрутер (Recruiter)**: чтение результатов и отчётов
- **Оператор (Operator)**: загрузка данных, запуск оценки, просмотр результатов

## ML-модуль

Базовая модель: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`

Веса категорий оценки:
- Навыки: 40%
- Опыт: 30%
- Структура: 20%
- ATS-совместимость: 10%

Пороги рекомендаций:
- ≥ 75: «Пригласить немедленно»
- 50-74: «Отложить на рассмотрение»
- < 50: «Отклонить»

## Разработка

Все инструкции для разработки находятся в [CLAUDE.md](CLAUDE.md)

Контекст проекта: [CONTEXT.md](CONTEXT.md)

## Лицензия

MIT
