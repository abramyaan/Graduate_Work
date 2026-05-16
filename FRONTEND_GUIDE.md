# Руководство по фронтенду

## Обзор

Фронтенд построен на **React 18** с **TypeScript**, **Vite** в качестве сборщика, **Tailwind CSS** для стилизации и **Recharts** для визуализации данных.

## Быстрый старт

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Приложение откроется на http://localhost:5173

## Структура проекта

```
frontend/
├── src/
│   ├── api/                   # API клиенты
│   │   ├── client.ts          # Axios instance с interceptors
│   │   ├── auth.ts            # Авторизация
│   │   ├── vacancies.ts       # Работа с вакансиями
│   │   └── evaluations.ts     # Результаты оценки
│   │
│   ├── components/            # Переиспользуемые компоненты
│   │   ├── Layout.tsx         # Главный layout с навигацией
│   │   ├── ProtectedRoute.tsx # HOC для защищённых маршрутов
│   │   ├── LoadingSpinner.tsx # Индикатор загрузки
│   │   ├── ScoreCard.tsx      # Карточка с баллом
│   │   ├── ErrorMessage.tsx   # Компонент ошибки
│   │   ├── EmptyState.tsx     # Пустое состояние
│   │   └── index.ts           # Экспорты компонентов
│   │
│   ├── hooks/                 # Custom React hooks
│   │   └── useAuth.ts         # Хук авторизации
│   │
│   ├── pages/                 # Страницы приложения
│   │   ├── Login.tsx          # Страница входа
│   │   ├── Dashboard.tsx      # Дашборд с вакансиями
│   │   ├── Results.tsx        # Таблица результатов
│   │   └── CandidateDetail.tsx # Детальная карточка кандидата
│   │
│   ├── types/                 # TypeScript типы
│   │   └── index.ts           # API интерфейсы
│   │
│   ├── utils/                 # Утилиты
│   │   ├── constants.ts       # Константы приложения
│   │   ├── format.ts          # Форматирование данных
│   │   └── download.ts        # Скачивание файлов
│   │
│   ├── App.tsx                # Главный компонент с роутингом
│   ├── main.tsx               # Точка входа
│   └── index.css              # Глобальные стили + Tailwind
│
├── .env                       # Переменные окружения
├── .env.example               # Пример .env
├── .eslintrc.cjs              # Конфигурация ESLint
├── .gitignore                 # Git ignore
├── index.html                 # HTML шаблон
├── package.json               # Зависимости
├── postcss.config.js          # PostCSS конфигурация
├── tailwind.config.js         # Tailwind конфигурация
├── tsconfig.json              # TypeScript конфигурация
├── vite.config.ts             # Vite конфигурация
└── README.md                  # Документация

```

## Основные страницы

### 1. Login (`/login`)
- Форма авторизации
- Сохранение JWT токена в localStorage
- Редирект на Dashboard после входа

### 2. Dashboard (`/dashboard`)
- Список активных вакансий
- Кнопка запуска оценки
- Переход к результатам

### 3. Results (`/results/:vacancyId`)
- Таблица кандидатов по вакансии
- Цветовая индикация по баллам:
  - **Зелёный** (≥75): "Пригласить немедленно"
  - **Жёлтый** (50-74): "Отложить"
  - **Красный** (<50): "Отклонить"
- Экспорт в PDF/Excel

### 4. CandidateDetail (`/candidate/:evaluationId`)
- Детальная информация о кандидате
- Графики (столбчатая и радарная диаграммы)
- Детализация по категориям оценки

## API интеграция

### Axios конфигурация
- Базовый URL: `VITE_API_BASE_URL`
- JWT токен автоматически добавляется к запросам
- При 401 — автоматический logout и редирект

### Endpoints
- `POST /api/auth/login` — авторизация
- `GET /api/auth/me` — текущий пользователь
- `GET /api/vacancies` — список вакансий
- `GET /api/evaluations/vacancy/{id}` — результаты по вакансии
- `GET /api/evaluations/{id}` — детали оценки
- `POST /api/evaluations/run/{id}` — запуск оценки
- `GET /api/evaluations/export/{id}?format=pdf|excel` — экспорт

## Стилизация

### Tailwind CSS
Используется Tailwind CSS v4 для всех стилей.

#### Основные цвета:
- **Primary**: Blue (blue-500, blue-600)
- **Success**: Green (green-500, green-600)
- **Warning**: Yellow (yellow-500, yellow-600)
- **Danger**: Red (red-500, red-600)

#### Компоненты:
- Кнопки: `bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg`
- Карточки: `bg-white shadow-md rounded-lg p-6`
- Таблицы: `min-w-full divide-y divide-gray-200`

## Визуализация данных

### Recharts
Используется для графиков:
- **BarChart**: баллы по категориям
- **RadarChart**: профиль кандидата

Пример:
```tsx
<ResponsiveContainer width="100%" height={300}>
  <BarChart data={data}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="category" />
    <YAxis domain={[0, 100]} />
    <Tooltip />
    <Bar dataKey="score" fill="#3b82f6" />
  </BarChart>
</ResponsiveContainer>
```

## Типизация

Все компоненты строго типизированы TypeScript.

### Основные интерфейсы:
```typescript
interface User {
  id: number;
  username: string;
  email: string;
  role: 'Admin' | 'Recruiter' | 'Operator';
}

interface EvaluationResult {
  id: number;
  candidate: Candidate;
  vacancy: Vacancy;
  overall_score: number;
  skills_score: number;
  experience_score: number;
  structure_score: number;
  ats_score: number;
  recommendation: string;
}
```

## Роутинг

Используется React Router v6:
```tsx
<Route path="/login" element={<Login />} />
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />
```

## Защищённые маршруты

`ProtectedRoute` компонент проверяет наличие токена:
```tsx
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  if (!token) return <Navigate to="/login" />;
  return children;
};
```

## Разработка

### Запуск dev-сервера
```bash
npm run dev
```

### Сборка
```bash
npm run build
```

### Линтинг
```bash
npm run lint
```

### Предпросмотр production
```bash
npm run preview
```

## Соглашения по коду

1. **Именование**:
   - Компоненты: PascalCase (`Dashboard.tsx`)
   - Хуки: camelCase с префиксом `use` (`useAuth.ts`)
   - Утилиты: camelCase (`format.ts`)

2. **Структура компонента**:
```tsx
import React from 'react';

interface Props {
  // ...
}

const Component: React.FC<Props> = ({ prop }) => {
  // state
  // effects
  // handlers
  
  return (
    // JSX
  );
};

export default Component;
```

3. **Импорты**:
```tsx
// React
import React, { useState, useEffect } from 'react';

// Библиотеки
import axios from 'axios';

// Локальные модули
import { Component } from '../components';
import { apiClient } from '../api/client';
import { User } from '../types';
```

4. **Типизация**:
   - Всегда указывайте типы для props
   - Используйте интерфейсы вместо типов для объектов
   - Избегайте `any` (используйте `unknown` если необходимо)

## Обработка ошибок

```tsx
try {
  const data = await api.getData();
  setData(data);
} catch (err: any) {
  setError(err.response?.data?.detail || err.message);
}
```

## Экспорт данных

```tsx
const handleExport = async (format: 'pdf' | 'excel') => {
  const blob = await evaluationsApi.exportResults(id, format);
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `results.${format}`;
  a.click();
};
```

## Оптимизация

1. **Lazy loading** страниц:
```tsx
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
```

2. **Мемоизация** тяжёлых вычислений:
```tsx
const memoizedValue = useMemo(() => computeExpensive(data), [data]);
```

3. **Debounce** для поиска:
```tsx
const debouncedSearch = useMemo(
  () => debounce((value) => search(value), 300),
  []
);
```

## Тестирование

Для тестирования рекомендуется использовать:
- **Vitest** — unit тесты
- **Testing Library** — компонентные тесты
- **Playwright** — E2E тесты

## Развёртывание

### Production build
```bash
npm run build
```

Результат в папке `dist/`.

### Переменные окружения
```env
VITE_API_BASE_URL=https://api.production.com/api
```

### Nginx конфигурация
```nginx
server {
  listen 80;
  server_name example.com;
  root /var/www/frontend/dist;
  
  location / {
    try_files $uri $uri/ /index.html;
  }
  
  location /api {
    proxy_pass http://backend:8000;
  }
}
```

## Troubleshooting

### Проблема: CORS ошибки
**Решение**: Убедитесь, что backend настроен на разрешение CORS для фронтенд домена.

### Проблема: 401 после обновления страницы
**Решение**: Проверьте, что токен сохраняется в localStorage и не истёк.

### Проблема: Графики не отображаются
**Решение**: Убедитесь, что данные приходят в правильном формате для Recharts.

## Полезные команды

```bash
# Установка зависимостей
npm install

# Обновление зависимостей
npm update

# Проверка устаревших пакетов
npm outdated

# Аудит безопасности
npm audit

# Исправление уязвимостей
npm audit fix
```
