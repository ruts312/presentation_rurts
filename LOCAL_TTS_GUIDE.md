# 🚀 Локальный запуск с TTS

## ✅ Локальный TTS работает!

Модель `kyrgyz-ai/TTS_small` успешно запущена локально.
Тестовый файл: `test_slide_1_audio.wav` (841KB)

## Запуск локально

```bash
# Backend
cd backend
set USE_LOCAL_TTS=true
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Frontend
cd frontend
npm run dev
```

## 📦 Деплой на Railway

### 1. Подготовка

Railway не поддерживает тяжелые ML модели на бесплатном плане.
Используйте `requirements-production.txt`:

```bash
# В railway.toml или настройках
BUILD_COMMAND=pip install -r backend/requirements-production.txt
```

### 2. Переменные окружения

```
USE_LOCAL_TTS=false
OPENAI_API_KEY=your_key
REDIS_HOST=your_redis_host
REDIS_PORT=6379
```

### 3. Деплой команды

```bash
# Через Railway CLI
railway login
railway link
railway up

# Или через GitHub
# Подключите репозиторий в Railway Dashboard
```

### 4. Frontend на Vercel

```bash
cd frontend
vercel --prod
```

Обновите API_URL в `frontend/src/services/api.ts`:
```typescript
const API_URL = 'https://your-app.railway.app'
```

## 🔊 TTS Варианты

- **Локально**: Работает! (841KB реальное аудио)
- **Railway**: USE_LOCAL_TTS=false (mock audio)
- **Production**: Используйте Google Cloud TTS или Azure TTS

## 📝 Важно

Первая загрузка модели занимает ~1 минуту (скачивает 332MB)
Дальше модель кешируется локально в `~/.cache/huggingface`
