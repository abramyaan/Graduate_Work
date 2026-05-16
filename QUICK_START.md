# 🚀 Быстрый старт системы

Полная инструкция по запуску ПИС «Интеллектуальная оценка резюме на соответствие вакансии».

## Предварительные требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Git

## Шаг 1: Клонирование и настройка

```bash
# Клонируйте репозиторий (если ещё не сделано)
cd GraduateWork

# Создайте виртуальное окружение Python
python -m venv venv

# Активируйте его
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости Python
pip install -r requirements.txt

# Установите зависимости фронтенда
cd frontend
npm install
cd ..
```

## Шаг 2: База данных

### 2.1 Запуск PostgreSQL

**Вариант A: Локально**
```bash
# Убедитесь, что PostgreSQL запущен
# Windows:
net start postgresql-x64-14

# Linux:
sudo systemctl start postgresql
```

**Вариант B: Docker**
```bash
docker-compose up -d postgres
```

### 2.2 Создание БД

```sql
-- Подключитесь к PostgreSQL
psql -U postgres

-- Создайте базу данных
CREATE DATABASE resume_db;

-- Создайте пользователя (опционально)
CREATE USER resume_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE resume_db TO resume_user;
```

### 2.3 Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# База данных (pg8000 драйвер)
DATABASE_URL=postgresql+pg8000://resume_user:strong_password@localhost:5432/resume_db

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ML модель
MODEL_PATH=ml/models/finetuned_model

# API
API_HOST=0.0.0.0
API_PORT=8000

# Фронтенд (для VITE)
VITE_API_BASE_URL=http://localhost:8000/api
```

## Шаг 3: Инициализация БД

### 3.1 Создание справочных данных

```bash
# Из корня проекта
python -m backend.scripts.init_data
```

Создаст:
- ✅ Роли: Администратор, Рекрутер, Оператор
- ✅ Категории оценки: Навыки (40%), Опыт (30%), Структура (20%), ATS (10%)
- ✅ Правила рекомендаций: >= 75, 50-74, < 50

### 3.2 Создание администратора

```bash
python -m backend.scripts.create_admin
```

Создаст тестового пользователя:
- **Логин:** `admin`
- **Пароль:** `admin123`
- **Роль:** Администратор

⚠️ **Важно:** Смените пароль после первого входа в production!

## Шаг 4: Запуск backend

```bash
# Из корня проекта
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend будет доступен на: **http://localhost:8000**

API документация (Swagger): **http://localhost:8000/docs**

## Шаг 5: Запуск frontend

```bash
# В новом терминале
cd frontend
npm run dev
```

Frontend откроется на: **http://localhost:5173**

## Шаг 6: Вход в систему

1. Откройте браузер: http://localhost:5173
2. Вы будете перенаправлены на страницу входа
3. Введите:
   - **Логин:** `admin`
   - **Пароль:** `admin123`
4. Нажмите **Войти**

✅ Вы попадёте на дашборд!

## Структура системы

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Frontend  │─────→│   Backend   │─────→│  PostgreSQL │
│   React     │      │   FastAPI   │      │     БД      │
│   :5173     │      │   :8000     │      │   :5432     │
└─────────────┘      └─────────────┘      └─────────────┘
```

## Проверка работы

### Backend

```bash
# Проверка здоровья API
curl http://localhost:8000/health

# Проверка документации
curl http://localhost:8000/docs
```

### Frontend

Откройте: http://localhost:5173

Должна открыться страница входа.

### База данных

```bash
# Подключение к БД
psql -U resume_user -d resume_db

# Проверка таблиц
\dt

# Проверка пользователей
SELECT login, email, last_name, first_name FROM user_account;

# Проверка ролей
SELECT * FROM user_role;
```

## Порты по умолчанию

| Сервис | Порт | URL |
|--------|------|-----|
| Frontend | 5173 | http://localhost:5173 |
| Backend API | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| PostgreSQL | 5432 | postgresql://localhost:5432 |

## Тестовые данные

После входа в систему вы можете:

1. **Создать вакансию** (если есть соответствующий функционал в backend)
2. **Загрузить резюме**
3. **Запустить оценку**
4. **Посмотреть результаты**

## Troubleshooting

### Backend не запускается

**Ошибка:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Решение:**
1. Проверьте, что PostgreSQL запущен
2. Проверьте `DATABASE_URL` в `.env`
3. Проверьте, что БД `resume_db` создана

### Frontend не может подключиться к backend

**Ошибка:** `Network Error` или CORS

**Решение:**
1. Убедитесь, что backend запущен на порту 8000
2. Проверьте `VITE_API_BASE_URL` в `frontend/.env`
3. Проверьте CORS настройки в `backend/main.py`

### Не получается войти

**Ошибка:** `401 Unauthorized`

**Решение:**
1. Убедитесь, что администратор создан: `python -m backend.scripts.create_admin`
2. Проверьте логин/пароль: `admin` / `admin123`
3. Проверьте логи backend в консоли

### Таблицы не созданы

**Решение:**
```bash
# Запустите инициализацию
python -m backend.scripts.init_data

# Или создайте таблицы вручную
python -c "from backend.db.database import engine; from backend.models.models import Base; Base.metadata.create_all(bind=engine)"
```

## Следующие шаги

После успешного запуска:

1. **Измените пароль администратора**
2. **Создайте других пользователей** (рекрутеров, операторов)
3. **Настройте ML модель** (см. `ml/train.py`)
4. **Добавьте тестовые данные** (вакансии, резюме)
5. **Протестируйте функционал оценки**

## Документация

| Файл | Описание |
|------|----------|
| `README.md` | Общая информация о проекте |
| `CLAUDE.md` | Инструкции для разработки |
| `DATABASE_SCHEMA.md` | Схема БД (18 таблиц) |
| `FRONTEND_START.md` | Запуск фронтенда |
| `FRONTEND_GUIDE.md` | Руководство по фронтенду |
| `backend/scripts/README.md` | Инструкции по скриптам БД |

## Полезные команды

```bash
# Backend
uvicorn backend.main:app --reload           # Запуск с hot-reload
python -m pytest backend/tests/             # Тесты
black backend/                              # Форматирование
ruff check backend/                         # Линтинг

# Frontend
npm run dev                                 # Разработка
npm run build                               # Production сборка
npm run lint                                # Проверка кода

# База данных
python -m backend.scripts.init_data         # Инициализация справочников
python -m backend.scripts.create_admin      # Создание администратора

# ML
python ml/train.py                          # Обучение модели
python ml/evaluate.py                       # Оценка резюме

# Docker
docker-compose up -d                        # Запуск всех сервисов
docker-compose down                         # Остановка
docker-compose logs -f backend              # Логи backend
```

## Production деплой

Для production используйте:
- **Backend:** Gunicorn + Nginx
- **Frontend:** Статическая сборка (nginx)
- **БД:** Managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
- **ML модель:** Загружайте при старте backend
- **Секреты:** Используйте переменные окружения, не коммитьте `.env`

См. `docker-compose.yml` для примера production-конфигурации.

---

**Готово! Система запущена и готова к использованию.** 🎉

Если возникли проблемы, проверьте:
- Логи backend в консоли
- Консоль браузера (F12) для ошибок frontend
- Логи PostgreSQL
