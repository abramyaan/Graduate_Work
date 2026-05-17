@echo off
echo ========================================
echo Starting Frontend Server
echo ========================================
echo.

REM Переход в директорию frontend
cd frontend

REM Запуск Vite dev server
echo Starting Vite dev server on http://localhost:5173
echo Press Ctrl+C to stop
echo.
npm run dev

pause
