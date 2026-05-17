@echo off
echo ========================================
echo Starting Backend Server
echo ========================================
echo.

REM Активация виртуального окружения
call venv\Scripts\activate.bat

REM Запуск FastAPI сервера
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

pause
