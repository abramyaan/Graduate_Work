# 📝 Использование скриптов БД

Краткая памятка по использованию скриптов для работы с базой данных.

## Список скриптов

| Скрипт | Назначение | Команда |
|--------|-----------|---------|
| `check_db.py` | Проверка подключения к БД | `python -m backend.scripts.check_db` |
| `init_data.py` | Инициализация справочных данных | `python -m backend.scripts.init_data` |
| `create_admin.py` | Создание администратора | `python -m backend.scripts.create_admin` |

## Порядок использования

### 1️⃣ Проверка подключения

**Когда использовать:** Перед любыми операциями с БД

```bash
python -m backend.scripts.check_db
```

**Что проверяет:**
- ✅ Подключение к PostgreSQL
- ✅ Версию PostgreSQL
- ✅ Текущую базу данных
- ✅ Количество таблиц
- ✅ Наличие справочных данных
- ✅ Количество пользователей

**Пример вывода:**
```
============================================================
Проверка подключения к PostgreSQL
============================================================

📊 Параметры подключения:
   Хост: localhost:5432/resume_db
   Пользователь: resume_user

🔌 Попытка подключения...
✅ Подключение успешно!

🐘 PostgreSQL версия:
   PostgreSQL 14.5 on x86_64-pc-linux-gnu...

🔍 Проверка сессии...
   База данных: resume_db
   Таблиц в БД: 18
   ✅ Структура БД полная (18 таблиц)

📋 Проверка справочных данных:
   Ролей: 3 ✅
   Категорий оценки: 4 ✅
   Правил рекомендаций: 3 ✅
   Пользователей: 1

============================================================
✅ Проверка завершена успешно
============================================================
```

### 2️⃣ Инициализация справочников

**Когда использовать:** Первый запуск или после пересоздания БД

```bash
python -m backend.scripts.init_data
```

**Что создаёт:**

1. **Роли пользователей:**
   - Администратор (Admin)
   - Рекрутер (Recruiter)
   - Оператор (Operator)

2. **Категории оценки:**
   - Навыки (40%)
   - Опыт (30%)
   - Структура резюме (20%)
   - ATS-совместимость (10%)

3. **Правила рекомендаций:**
   - >= 75: "Пригласить немедленно"
   - 50-74: "Отложить"
   - < 50: "Отклонить"

**Особенности:**
- ✅ Идемпотентный (можно запускать несколько раз)
- ✅ Не создаёт дубликаты
- ✅ Обновляет изменённые значения

### 3️⃣ Создание администратора

**Когда использовать:** После инициализации справочников

```bash
python -m backend.scripts.create_admin
```

**Что создаёт:**

Пользователя с параметрами:
- **Логин:** `admin`
- **Пароль:** `admin123` (хэш bcrypt)
- **Email:** `admin@system.local`
- **ФИО:** Администратор Системный
- **Роль:** Администратор

**Пример вывода:**
```
============================================================
✅ Администратор успешно создан!
============================================================

📋 Данные для входа:
   Логин:    admin
   Пароль:   admin123
   Email:    admin@system.local
   ФИО:      Администратор Системный
   Роль:     Администратор
   User ID:  1
   Дата рег: 2026-05-16

🚀 Теперь можно войти в систему через фронтенд!
============================================================
```

**⚠️ Важно:** Если пользователь уже существует, скрипт не будет его пересоздавать.

## Типичные сценарии

### Первый запуск системы

```bash
# 1. Проверка подключения
python -m backend.scripts.check_db

# 2. Инициализация справочников
python -m backend.scripts.init_data

# 3. Создание администратора
python -m backend.scripts.create_admin

# 4. Финальная проверка
python -m backend.scripts.check_db
```

### После изменения схемы БД

```bash
# 1. Удалите все таблицы (если нужно)
# SQL: DROP SCHEMA public CASCADE; CREATE SCHEMA public;

# 2. Заново создайте структуру
python -m backend.scripts.init_data

# 3. Создайте пользователей
python -m backend.scripts.create_admin
```

### Проверка состояния БД

```bash
# Быстрая проверка
python -m backend.scripts.check_db
```

### Создание дополнительных пользователей

**Вариант A:** Модифицируйте `create_admin.py`

```python
# В конце файла измените параметры
if __name__ == "__main__":
    create_admin_user(
        login="recruiter1",
        password="rec123",
        email="recruiter@company.com",
        last_name="Петров",
        first_name="Пётр"
    )
```

**Вариант B:** Используйте SQL

```sql
-- Получите ID роли
SELECT role_id FROM user_role WHERE role_name = 'Рекрутер';

-- Создайте пользователя (используйте хэш из другого пользователя для теста)
INSERT INTO user_account (
    login, 
    password_hash, 
    email, 
    last_name, 
    first_name,
    registration_date,
    role_id
) VALUES (
    'recruiter1',
    '$2b$12$...',  -- Хэш от пароля
    'recruiter@company.com',
    'Петров',
    'Пётр',
    CURRENT_DATE,
    2  -- ID роли Рекрутер
);
```

## Переменные окружения

Убедитесь, что файл `.env` настроен:

```env
DATABASE_URL=postgresql+pg8000://user:password@localhost:5432/resume_db
```

Скрипты используют эту переменную для подключения к БД.

## Troubleshooting

### Ошибка: "ModuleNotFoundError: No module named 'backend'"

**Причина:** Запуск не из корня проекта

**Решение:**
```bash
# Перейдите в корень проекта
cd /path/to/GraduateWork

# Запустите скрипт
python -m backend.scripts.check_db
```

### Ошибка: "could not connect to server"

**Причина:** PostgreSQL не запущен или неверные параметры

**Решение:**
1. Запустите PostgreSQL
2. Проверьте `DATABASE_URL` в `.env`
3. Создайте БД: `CREATE DATABASE resume_db;`

### Ошибка: "relation does not exist"

**Причина:** Таблицы не созданы

**Решение:**
```bash
python -m backend.scripts.init_data
```

### Ошибка: "duplicate key value violates unique constraint"

**Причина:** Пользователь уже существует

**Решение:**

Либо используйте существующего пользователя, либо удалите его:

```sql
DELETE FROM user_account WHERE login = 'admin';
```

Затем создайте заново:
```bash
python -m backend.scripts.create_admin
```

## Автоматизация

### Bash скрипт

Создайте `scripts/setup_db.sh`:

```bash
#!/bin/bash

echo "🔧 Настройка базы данных..."

# Проверка подключения
python -m backend.scripts.check_db || exit 1

# Инициализация
python -m backend.scripts.init_data || exit 1

# Создание администратора
python -m backend.scripts.create_admin || exit 1

# Финальная проверка
python -m backend.scripts.check_db

echo "✅ База данных готова к использованию!"
```

Использование:
```bash
chmod +x scripts/setup_db.sh
./scripts/setup_db.sh
```

### Windows Batch скрипт

Создайте `scripts/setup_db.bat`:

```batch
@echo off
echo Настройка базы данных...

python -m backend.scripts.check_db
if errorlevel 1 exit /b 1

python -m backend.scripts.init_data
if errorlevel 1 exit /b 1

python -m backend.scripts.create_admin
if errorlevel 1 exit /b 1

python -m backend.scripts.check_db

echo База данных готова к использованию!
```

Использование:
```batch
scripts\setup_db.bat
```

## Дополнительная информация

- **Подробная документация:** `backend/scripts/README.md`
- **Схема БД:** `DATABASE_SCHEMA.md`
- **Быстрый старт:** `QUICK_START.md`

---

**Готово к использованию!** 🚀
