@echo off
echo ========================================
echo Australian Super Source - Full Stack
echo ========================================
echo.
echo Starting both Backend and Frontend...
echo.

REM Start Backend
echo [1/2] Starting Flask Backend...
start "Flask Backend" cmd /k "cd /d "%~dp0Backend" && run.bat"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend
echo [2/2] Starting React Frontend...
start "React Frontend" cmd /k "cd /d "%~dp0client" && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo ========================================
echo.
echo Backend API:  http://localhost:5000
echo Frontend:     http://localhost:5173
echo.
echo Press any key to exit this window
echo (The servers will continue running)
echo.
pause >nul
