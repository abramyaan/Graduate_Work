# Инструкция по запуску проекта

## Что было исправлено

1. **CORS настройки** - уже настроены правильно в `backend/main.py`
2. **Эндпоинт детальных результатов** - исправлена схема ответа `/api/results/{id}` для совместимости с фронтендом
3. **Экспорт в PDF и Excel** - добавлены эндпоинты `/api/results/export/{vacancy_id}?format=pdf|excel`
4. **Типы TypeScript** - обновлены для совместимости с бэкендом

## Запуск проекта

### 1. Установка зависимостей (если еще не установлены)

```bash
# Активировать виртуальное окружение
venv\Scripts\Activate.ps1

# Установить зависимости Python
pip install -r requirements.txt

# Установить зависимости фронтенда
cd frontend
npm install
cd ..
```

### 2. Запуск базы данных

```bash
# Запустить PostgreSQL через Docker
docker-compose up -d postgres
```

### 3. Запуск бэкенда

В первом терминале:

```powershell
# Активировать виртуальное окружение
venv\Scripts\Activate.ps1

# Запустить FastAPI сервер
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Бэкенд будет доступен на http://localhost:8000

### 4. Запуск фронтенда

Во втором терминале:

```bash
cd frontend
npm run dev
```

Фронтенд будет доступен на http://localhost:5173

## Проверка работы

1. Откройте http://localhost:5173
2. Войдите в систему (используйте существующего пользователя из БД)
3. Загрузите резюме для вакансии
4. Запустите оценку
5. Перейдите в "Результаты"
6. Нажмите "Подробнее" на любом результате - должна открыться страница с деталями
7. Попробуйте экспортировать результаты в PDF или Excel

## Возможные проблемы

### Ошибка: ModuleNotFoundError: No module named 'PyPDF2'

**Решение:** Активируйте виртуальное окружение и установите зависимости:
```powershell
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Ошибка: CORS policy

**Решение:** Убедитесь что:
1. Бэкенд запущен на порту 8000
2. Фронтенд запущен на порту 5173
3. В `frontend/src/api/client.ts` baseURL указан как `http://localhost:8000/api`

### Ошибка: Failed to load resource: net::ERR_CONNECTION_REFUSED

**Решение:** Бэкенд не запущен. Запустите его:
```powershell
venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Экспорт PDF не работает

Если reportlab не установлен, система автоматически предложит использовать формат Excel.
Для установки reportlab:
```bash
pip install reportlab==4.0.9
```

### Экспорт Excel возвращает CSV

Если openpyxl не установлен, система автоматически вернет CSV файл (который можно открыть в Excel).
Для полноценного Excel:
```bash
pip install openpyxl==3.1.2
```

## Структура API эндпоинтов

- `GET /api/results/?vacancy_id={id}` - список результатов по вакансии
- `GET /api/results/{result_id}` - детальный результат оценки
- `GET /api/results/export/{vacancy_id}?format=pdf` - экспорт в PDF
- `GET /api/results/export/{vacancy_id}?format=excel` - экспорт в Excel
- `POST /api/results/evaluate` - запуск оценки резюме

## Примечания

1. Первый запуск бэкенда занимает 10-30 секунд из-за загрузки ML модели
2. Если модель не найдена, бэкенд всё равно запустится, но оценка будет недоступна
3. Для обучения модели запустите `python ml/train.py`
