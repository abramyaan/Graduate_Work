@echo off
echo ========================================
echo Starting Graduate Work Project
echo ========================================
echo.

echo 1. Starting PostgreSQL via Docker...
docker-compose up -d postgres
echo PostgreSQL started!
echo.

echo 2. Starting Backend server...
start "Backend Server" cmd /k start_backend.bat
timeout /t 3 /nobreak > nul
echo.

echo 3. Starting Frontend server...
start "Frontend Server" cmd /k start_frontend.bat
echo.

echo ========================================
echo All servers started!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to stop all servers...
pause > nul

echo.
echo Stopping servers...
docker-compose down
taskkill /FI "WINDOWTITLE eq Backend Server*" /F
taskkill /FI "WINDOWTITLE eq Frontend Server*" /F
echo.
echo All servers stopped.
pause
