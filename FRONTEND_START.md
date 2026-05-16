# 🚀 Быстрый старт фронтенда

## Создано

✅ **Полное React-приложение** для системы оценки резюме:
- 4 страницы (Login, Dashboard, Results, CandidateDetail)
- TypeScript + Tailwind CSS + Recharts
- JWT авторизация
- API интеграция
- Визуализация данных

## Запуск за 3 шага

### 1️⃣ Установка зависимостей
```bash
cd frontend
npm install
```

### 2️⃣ Проверка настроек
```bash
node check-setup.cjs
```

Должно показать: `✅ Все проверки пройдены!`

### 3️⃣ Запуск
```bash
npm run dev
```

Откроется: **http://localhost:5173**

## Структура

```
frontend/src/
├── api/          # HTTP клиенты (axios)
├── components/   # Переиспользуемые компоненты
├── pages/        # 4 основные страницы
├── types/        # TypeScript интерфейсы
├── utils/        # Утилиты
└── hooks/        # Custom hooks
```

## Страницы

| URL | Страница | Описание |
|-----|----------|----------|
| `/login` | Login | Форма входа |
| `/dashboard` | Dashboard | Список вакансий |
| `/results/:id` | Results | Таблица кандидатов |
| `/candidate/:id` | CandidateDetail | Карточка + графики |

## API

Frontend ожидает backend на: `http://localhost:8000/api`

Настроить в файле `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Команды

```bash
npm run dev      # Разработка (http://localhost:5173)
npm run build    # Production сборка
npm run preview  # Просмотр production
npm run lint     # Проверка кода
```

## Документация

| Файл | Описание |
|------|----------|
| `frontend/README.md` | Подробная документация |
| `frontend/CHECKLIST.md` | Чеклист проверки |
| `FRONTEND_GUIDE.md` | Руководство разработчика |
| `FRONTEND_OVERVIEW.md` | Обзор архитектуры |

## Что дальше?

1. ✅ **Frontend готов** — все файлы созданы
2. 🔨 **Запустите backend** (FastAPI на порту 8000)
3. 🚀 **Запустите frontend** (`npm run dev`)
4. 🧪 **Протестируйте**:
   - Откройте http://localhost:5173
   - Войдите через /login (если backend работает)
   - Проверьте все страницы

## Проблемы?

### CORS ошибки
Backend должен разрешить запросы с `http://localhost:5173`

### 401 Unauthorized
Проверьте, что backend запущен и пользователь создан в БД

### Графики не отображаются
Проверьте, что recharts установлен: `npm list recharts`

## Технологии

- React 18
- TypeScript 5.3
- Vite 5.0
- Tailwind CSS 4.3
- Recharts 3.8
- React Router 6.21
- Axios 1.6

## Статистика

- 📁 **20** исходных файлов TypeScript/TSX
- 📄 **4** основные страницы
- 🧩 **7** компонентов
- 🌐 **3** API клиента
- 🪝 **1** custom hook
- 📊 **2** типа графиков

---

**Готово к использованию!** 🎉

Для деталей см. `frontend/README.md`
