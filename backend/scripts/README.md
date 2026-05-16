# Скрипты управления БД

Набор скриптов для инициализации и управления базой данных системы оценки резюме.

## Структура

```
backend/scripts/
├── __init__.py          # Инициализация пакета
├── init_data.py         # Инициализация справочных данных
├── create_admin.py      # Создание тестового администратора
└── README.md            # Этот файл
```

## Порядок запуска

### 1️⃣ Инициализация справочных данных

Создаёт в БД:
- Роли пользователей (Администратор, Рекрутер, Оператор)
- Категории оценки с весами (Навыки 40%, Опыт 30%, Структура 20%, ATS 10%)
- Правила рекомендаций (>= 75: "Пригласить", 50-74: "Отложить", < 50: "Отклонить")

```bash
# Из корня проекта
python -m backend.scripts.init_data
```

**Вывод:**
```
============================================================
Инициализация справочных данных системы
============================================================

🔧 Создание структуры БД...
✅ Структура БД готова

📋 Инициализация ролей пользователей...
   ✅ Создана роль: Администратор (ID: 1)
   ✅ Создана роль: Рекрутер (ID: 2)
   ✅ Создана роль: Оператор (ID: 3)
✅ Роли пользователей инициализированы

⚖️  Инициализация категорий оценки...
   ✅ Создана категория: Навыки (вес: 40%, ID: 1)
   ✅ Создана категория: Опыт (вес: 30%, ID: 2)
   ✅ Создана категория: Структура резюме (вес: 20%, ID: 3)
   ✅ Создана категория: ATS-совместимость (вес: 10%, ID: 4)
✅ Категории оценки инициализированы (сумма весов: 1.00)

🎯 Инициализация правил рекомендаций...
   ✅ Создано правило: Пригласить немедленно (балл: 75-100, ID: 1)
   ✅ Создано правило: Отложить (балл: 50-75, ID: 2)
   ✅ Создано правило: Отклонить (балл: 0-50, ID: 3)
✅ Правила рекомендаций инициализированы

============================================================
✅ Инициализация завершена успешно!
============================================================

💡 Следующий шаг: создайте администратора
   python -m backend.scripts.create_admin
```

### 2️⃣ Создание администратора

Создаёт тестового пользователя с полными правами.

```bash
python -m backend.scripts.create_admin
```

**Параметры по умолчанию:**
- Логин: `admin`
- Пароль: `admin123`
- Email: `admin@system.local`
- Роль: Администратор

**Вывод:**
```
🔧 Инициализация системы

📝 Создание дополнительных ролей...
   ℹ️  Роль уже существует: Рекрутер
   ℹ️  Роль уже существует: Оператор
✅ Все роли проверены

============================================================
Создание тестового администратора
============================================================

1. Проверка структуры БД...
✅ Структура БД готова

2. Проверка роли 'Администратор'...
✅ Роль 'Администратор' уже существует (ID: 1)

3. Проверка пользователя 'admin'...

4. Хэширование пароля...
✅ Пароль захэширован (bcrypt, длина хэша: 60 символов)

5. Создание пользователя 'admin'...

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

## Требования

### База данных

Убедитесь, что PostgreSQL запущен и доступен. Параметры подключения берутся из `.env`:

```env
DATABASE_URL=postgresql+pg8000://user:password@localhost:5432/resume_db
```

### Python зависимости

Должны быть установлены:
```bash
pip install -r requirements.txt
```

Ключевые зависимости для скриптов:
- `sqlalchemy >= 2.0.36` — ORM
- `pg8000 >= 1.31.0` — драйвер PostgreSQL (чистый Python)
- `passlib[bcrypt] == 1.7.4` — хэширование паролей

## Использование в production

### ⚠️ Безопасность

**Для production:**

1. **Смените пароль администратора** сразу после первого входа
2. **Не используйте** стандартные логин/пароль (`admin`/`admin123`)
3. **Удалите** или отключите тестового администратора после создания реальных пользователей

### Создание кастомного администратора

Отредактируйте `create_admin.py`:

```python
if __name__ == "__main__":
    create_admin_user(
        login="your_login",           # Свой логин
        password="strong_password",   # Сильный пароль
        email="admin@yourcompany.com",
        last_name="Иванов",
        first_name="Иван",
        patronymic="Иванович"
    )
```

Или создайте отдельный скрипт с нужными параметрами.

## Проверка данных

### SQL запросы для проверки

```sql
-- Проверка ролей
SELECT * FROM user_role ORDER BY role_id;

-- Проверка пользователей
SELECT 
    u.user_id, 
    u.login, 
    u.email, 
    u.first_name, 
    u.last_name,
    r.role_name 
FROM user_account u
JOIN user_role r ON u.role_id = r.role_id
ORDER BY u.user_id;

-- Проверка категорий оценки
SELECT 
    category_id, 
    name, 
    weight,
    (weight * 100) as weight_percent
FROM evaluation_category 
ORDER BY weight DESC;

-- Проверка правил рекомендаций
SELECT 
    recommendation_id,
    min_score,
    max_score,
    recommendation_text
FROM recommendation_rule
ORDER BY min_score DESC;

-- Проверка суммы весов (должна быть 1.00)
SELECT SUM(weight) as total_weight FROM evaluation_category;
```

## Troubleshooting

### Ошибка: "cannot import name 'Base'"

**Причина:** Неверный PYTHONPATH или запуск не из корня проекта

**Решение:**
```bash
# Убедитесь, что запускаете из корня проекта
cd /path/to/GraduateWork
python -m backend.scripts.init_data
```

### Ошибка: "could not connect to server"

**Причина:** PostgreSQL не запущен или неверные параметры подключения

**Решение:**
1. Проверьте, что PostgreSQL запущен:
   ```bash
   # Linux/Mac
   sudo systemctl status postgresql
   
   # Windows (PowerShell)
   Get-Service postgresql*
   ```

2. Проверьте параметры в `.env`:
   ```env
   DATABASE_URL=postgresql+pg8000://user:password@localhost:5432/resume_db
   ```

### Ошибка: "Пользователь уже существует"

**Причина:** Пользователь с таким логином или email уже в БД

**Решение:**

Либо измените параметры в скрипте, либо удалите существующего пользователя:

```sql
-- SQL запрос для удаления
DELETE FROM user_account WHERE login = 'admin';
```

### Ошибка: "IntegrityError: duplicate key value"

**Причина:** Попытка создать дубликат справочной записи

**Решение:** Скрипты идемпотентны — можно запускать повторно. Они проверяют существующие записи и не создают дубликаты.

## Дополнительные скрипты

### Создание других пользователей

Создайте файл `create_user.py`:

```python
from backend.scripts.create_admin import create_admin_user

# Создание рекрутера
create_admin_user(
    login="recruiter1",
    password="rec123",
    email="recruiter@company.com",
    last_name="Петров",
    first_name="Пётр",
    patronymic="Петрович"
)
```

Затем вручную измените роль в БД:

```sql
UPDATE user_account 
SET role_id = (SELECT role_id FROM user_role WHERE role_name = 'Рекрутер')
WHERE login = 'recruiter1';
```

### Очистка БД

**⚠️ Осторожно: удаляет ВСЕ данные!**

```python
# clear_db.py
from backend.db.database import engine
from backend.models.models import Base

Base.metadata.drop_all(bind=engine)
print("✅ Все таблицы удалены")
```

## Автоматизация

### Docker Compose

Добавьте в `docker-compose.yml`:

```yaml
services:
  init-db:
    build: .
    command: >
      sh -c "
        python -m backend.scripts.init_data &&
        python -m backend.scripts.create_admin
      "
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql+pg8000://user:pass@postgres:5432/resume_db
```

### Makefile

```makefile
.PHONY: init-db create-admin

init-db:
	python -m backend.scripts.init_data

create-admin:
	python -m backend.scripts.create_admin

setup-db: init-db create-admin
	@echo "✅ База данных настроена"
```

Использование:
```bash
make setup-db
```

## Документация по моделям

См. `backend/models/models.py` — полное описание всех 18 таблиц БД.

См. `DATABASE_SCHEMA.md` — подробная схема БД с порядком создания таблиц.
