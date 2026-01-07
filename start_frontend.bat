@echo off
echo ========================================
echo Запуск Frontend (React + Vite)
echo ========================================
echo.

cd frontend

REM Проверка установки зависимостей
if not exist "node_modules\" (
    echo Установка зависимостей...
    call npm install
    echo.
)

echo.
echo ========================================
echo Frontend запущен на http://localhost:5173
echo ========================================
echo.

REM Запуск dev сервера
call npm run dev
