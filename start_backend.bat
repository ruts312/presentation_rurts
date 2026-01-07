@echo off
echo ========================================
echo Запуск Backend (FastAPI)
echo ========================================
echo.

cd backend

REM Проверка виртуального окружения
if not exist "venv\" (
    echo Создание виртуального окружения...
    python -m venv venv
    echo.
)

REM Активация виртуального окружения
echo Активация виртуального окружения...
call venv\Scripts\activate

REM Проверка установки зависимостей
echo Проверка зависимостей...
pip install -r requirements.txt --quiet

echo.
echo ========================================
echo Backend запущен на http://localhost:8000
echo API документация: http://localhost:8000/docs
echo ========================================
echo.

REM Запуск сервера
python main.py
