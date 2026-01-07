# Проверка работоспособности проекта

## Шаг 1: Проверка Python

```powershell
python --version
# Должно быть 3.11 или выше
```

## Шаг 2: Проверка Node.js

```powershell
node --version
# Должно быть 18 или выше

npm --version
# Должно быть 9 или выше
```

## Шаг 3: Проверка структуры проекта

```powershell
cd c:\Users\KK\Desktop\presentation_ruts
ls
```

Должны видеть:
- backend/
- frontend/
- start_all.bat
- README.md
- и другие файлы

## Шаг 4: Проверка Backend файлов

```powershell
cd backend
ls
```

Должны видеть:
- main.py
- requirements.txt
- routers/
- services/
- data/

## Шаг 5: Проверка Frontend файлов

```powershell
cd ..\frontend
ls
```

Должны видеть:
- package.json
- src/
- index.html
- vite.config.ts

## Шаг 6: Проверка слайдов

```powershell
Get-Content ..\backend\data\slides.json | ConvertFrom-Json | Select-Object -ExpandProperty slides | Measure-Object
```

Должно показать Count: 10

## Шаг 7: Попробуйте запустить Backend

```powershell
cd ..\backend

# Создать виртуальное окружение
python -m venv venv

# Активировать
.\venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Проверить импорты
python -c "import fastapi; print('FastAPI OK')"
python -c "import openai; print('OpenAI OK')"
python -c "import httpx; print('HTTPX OK')"
```

Все должно печатать "OK"

## Шаг 8: Попробуйте запустить Frontend

```powershell
cd ..\frontend

# Установить зависимости
npm install

# Проверить установку
npm list react
npm list typescript
npm list vite
```

Все должно показать версии без ошибок

## Шаг 9: Проверьте API ключи

```powershell
cd ..\backend
cat .env
```

Должен содержать:
```
OPENAI_API_KEY=sk-...
```

Если файла нет, создайте:
```powershell
copy .env.example .env
notepad .env
```

## Шаг 10: Финальная проверка - Запуск!

### Терминал 1:
```powershell
cd backend
.\venv\Scripts\activate
python main.py
```

Должно появиться:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Терминал 2:
```powershell
cd frontend
npm run dev
```

Должно появиться:
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

## Шаг 11: Проверка в браузере

Откройте: http://localhost:5173

Должны увидеть:
- Заголовок "Адам укуктары"
- Первый слайд презентации
- Кнопки навигации
- Кнопку "СТОП - Задать вопрос"

## Шаг 12: Проверка API

Откройте: http://localhost:8000/docs

Должны увидеть:
- Swagger UI
- Список всех endpoints
- Возможность тестировать API

## Проверка функционала

### ✅ Презентация
- [ ] Слайды отображаются
- [ ] Можно перелистывать вперед/назад
- [ ] Показывается номер слайда

### ✅ Аудио (если есть HuggingFace ключ)
- [ ] Слышно озвучку слайдов
- [ ] Можно паузить/остановить
- [ ] Прогресс бар работает

### ✅ Вопросы (если есть OpenAI ключ)
- [ ] Кнопка "СТОП" работает
- [ ] Можно записать голос
- [ ] Вопрос распознается
- [ ] Получен ответ
- [ ] Ответ озвучен

## Если что-то не работает

### Backend не запускается
```powershell
# Проверьте Python
python --version

# Переустановите зависимости
pip install --upgrade -r requirements.txt

# Проверьте порт 8000
netstat -ano | findstr :8000
```

### Frontend не запускается
```powershell
# Очистите кеш
npm cache clean --force

# Удалите node_modules и переустановите
rm -r node_modules
npm install

# Проверьте порт 5173
netstat -ano | findstr :5173
```

### API ошибки
```powershell
# Проверьте .env файл
cat backend\.env

# Проверьте логи backend
# Они в терминале где запущен python main.py
```

### Микрофон не работает
- Дайте браузеру разрешение на микрофон
- Используйте Chrome или Edge
- Проверьте микрофон в системе

## Логи для отладки

### Backend логи
Смотрите в терминале где запущен `python main.py`

### Frontend логи
1. Откройте DevTools (F12)
2. Перейдите в Console
3. Смотрите ошибки

### Network проверка
1. DevTools (F12) → Network
2. Обновите страницу
3. Проверьте запросы к /api/

## Все работает! ✅

Если все пункты выполнены и проверены - поздравляем! 

Проект полностью функционален и готов к использованию.

---

**Возникли проблемы?** См. [README.md](README.md) → "Устранение неполадок"
