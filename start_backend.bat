@echo off
echo ========================================
echo Запуск Backend (FastAPI)
echo ========================================
echo.

cd backend

REM Используем общее виртуальное окружение проекта: ..\.venv
REM (оно уже используется в tasks.json для генерации аудио)
set VENV_PY=..\.venv\Scripts\python.exe

if not exist "%VENV_PY%" (
    echo Виртуальное окружение не найдено: %VENV_PY%
    echo Создаю ..\.venv ...
    python -m venv ..\.venv
    echo.
)

REM Проверка установки зависимостей
echo Проверка зависимостей...
"%VENV_PY%" -m pip install -r requirements.txt

echo.
echo ========================================
echo Backend запущен на http://localhost:8000
echo API документация: http://localhost:8000/docs
echo ========================================
echo.

REM Запуск сервера
"%VENV_PY%" main.py
