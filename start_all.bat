@echo off
echo ========================================
echo Запуск полного приложения
echo ========================================
echo.
echo Запуск Backend и Frontend...
echo.

REM Запуск backend в новом окне
start "Backend Server" cmd /k "cd /d %~dp0 && start_backend.bat"

REM Ожидание запуска backend
timeout /t 5 /nobreak > nul

REM Запуск frontend в новом окне
start "Frontend Server" cmd /k "cd /d %~dp0 && start_frontend.bat"

echo.
echo ========================================
echo Оба сервера запущены!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo ========================================
echo.
echo Нажмите любую клавишу для выхода...
pause > nul
