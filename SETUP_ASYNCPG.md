# Настройка PostgreSQL с asyncpg

## Выполненные изменения

### 1. Обновлена конфигурация БД

**backend/core/config.py:**
```python
DATABASE_URL: str = "postgresql+asyncpg://user@127.0.0.1:5433/resume_db"
```

### 2. Переключено на async SQLAlchemy

**backend/db/database.py:**
- Асинхронный движок с `create_async_engine`
- Асинхронные сессии с `AsyncSessionLocal`
- Async dependency `get_db()` для FastAPI
- Сохранена синхронная версия для скриптов (с pg8000)

### 3. Применена схема БД

```bash
docker exec -i resume_postgres psql -U user -d resume_db < db/schema.sql
```

Создано:
- ✅ 18 таблиц
- ✅ 3 роли (Администратор, Рекрутер, Оператор)
- ✅ 4 категории оценки
- ✅ 3 правила рекомендаций

### 4. Создан администратор

**Данные для входа:**
- Логин: `admin`
- Пароль: `admin123`
- Email: `admin@system.local`
- Роль: Администратор

## Параметры подключения

### Docker PostgreSQL
- Хост: `127.0.0.1`
- Порт: `5433` (внешний)
- Пользователь: `user`
- База данных: `resume_db`

### Формат URL
```
postgresql+asyncpg://user@127.0.0.1:5433/resume_db
```

## Структура database.py

### Для FastAPI (async)
```python
from backend.db.database import get_db, AsyncSession

@app.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    return result.scalars().all()
```

### Для скриптов (sync с pg8000)
```python
from backend.db.database import SessionLocal

db = SessionLocal()
try:
    items = db.query(Item).all()
finally:
    db.close()
```

## Зависимости

**requirements.txt:**
```
sqlalchemy>=2.0.36
asyncpg>=0.31.0    # Для async API
pg8000>=1.31.0     # Для синхронных скриптов
```

## Проверка работы

### 1. Проверка подключения
```bash
docker exec resume_postgres psql -U user -d resume_db -c "\dt"
```

### 2. Проверка пользователя
```bash
docker exec resume_postgres psql -U user -d resume_db -c \
  "SELECT login, email, last_name FROM user_account WHERE login='admin';"
```

**Результат:**
```
 login |       email        |   last_name   
-------+--------------------+---------------
 admin | admin@system.local | Администратор
```

### 3. Запуск backend
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Запуск frontend
```bash
cd frontend && npm run dev
```

### 5. Вход в систему
- URL: http://localhost:5173
- Логин: `admin`
- Пароль: `admin123`

## Известные проблемы

### Проблема: passlib + bcrypt 5.0
При использовании `passlib[bcrypt]` возникает ошибка:
```
ValueError: password cannot be longer than 72 bytes
```

**Решение:** Использовать `bcrypt` напрямую:
```python
import bcrypt

password = b'admin123'
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
```

### Проблема: Эмодзи в Windows консоли
Скрипты с эмодзи выдают ошибку кодировки.

**Решение:** Использовать `create_admin_simple.py` вместо `create_admin.py`.

## SQL команды

### Создание пользователя вручную
```sql
-- Сгенерировать хэш в Python:
-- python -c "import bcrypt; print(bcrypt.hashpw(b'password', bcrypt.gensalt()).decode())"

INSERT INTO user_account (
    login, 
    password_hash, 
    email, 
    last_name, 
    first_name,
    registration_date,
    role_id
) VALUES (
    'newuser',
    '$2b$12$...',  -- хэш пароля
    'user@example.com',
    'Иванов',
    'Иван',
    CURRENT_DATE,
    2  -- ID роли
);
```

### Проверка данных
```sql
-- Роли
SELECT * FROM user_role ORDER BY role_id;

-- Пользователи
SELECT u.login, u.email, r.role_name 
FROM user_account u
JOIN user_role r ON u.role_id = r.role_id;

-- Категории оценки
SELECT name, weight FROM evaluation_category;

-- Правила рекомендаций
SELECT * FROM recommendation_rule ORDER BY min_score DESC;
```

## Миграция с psycopg2/pg8000 на asyncpg

### Изменения в коде

**Было (sync):**
```python
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items
```

**Стало (async):**
```python
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    items = result.scalars().all()
    return items
```

### Ключевые отличия

| Операция | Sync | Async |
|----------|------|-------|
| Сессия | `Session` | `AsyncSession` |
| Dependency | `get_db()` | `async get_db()` |
| Запрос | `db.query(Model)` | `await db.execute(select(Model))` |
| Результат | `.all()` | `.scalars().all()` |
| Коммит | `db.commit()` | `await db.commit()` |
| Откат | `db.rollback()` | `await db.rollback()` |

## Docker команды

### Запуск PostgreSQL
```bash
docker-compose up -d postgres
```

### Проверка логов
```bash
docker logs resume_postgres
```

### Подключение к БД
```bash
docker exec -it resume_postgres psql -U user -d resume_db
```

### Применение схемы
```bash
docker exec -i resume_postgres psql -U user -d resume_db < db/schema.sql
```

### Резервная копия
```bash
docker exec resume_postgres pg_dump -U user resume_db > backup.sql
```

### Восстановление
```bash
docker exec -i resume_postgres psql -U user -d resume_db < backup.sql
```

## Следующие шаги

1. ✅ База данных настроена
2. ✅ Схема применена
3. ✅ Администратор создан
4. 🔄 Обновить API эндпоинты на async
5. 🔄 Протестировать фронтенд
6. 🔄 Настроить ML модель

## Полезные ссылки

- [SQLAlchemy Async ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [asyncpg](https://github.com/MagicStack/asyncpg)

---

**Дата настройки:** 2026-05-16  
**Статус:** ✅ База данных готова к использованию
