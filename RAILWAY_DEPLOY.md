# Railway Deployment Guide

## Подготовка к деплою

1. Убедитесь что все файлы закоммичены в git
2. Railway автоматически определит Python проект

## Переменные окружения на Railway

Добавьте в Railway следующие переменные:

```
OPENAI_API_KEY=ваш_ключ_openai
HUGGINGFACE_API_KEY=ваш_ключ_huggingface
USE_LOCAL_TTS=false
REDIS_HOST=redis_host_от_railway
REDIS_PORT=6379
```

## Важно для Railway

⚠️ **TTS модель**: На Railway ставим `USE_LOCAL_TTS=false` потому что:
- Torch и модели занимают много места (~2GB)
- Для локального TTS нужно больше RAM
- Railway бесплатный план имеет ограничения

Для production рекомендуется:
1. Использовать внешний TTS сервис (Google Cloud TTS, Azure TTS)
2. Или Railway Pro план с большими ресурсами
3. Или отдельный сервис только для TTS

## Деплой команды

```bash
# Через Railway CLI
railway login
railway init
railway up

# Через GitHub
# Подключите репозиторий в Railway Dashboard
```

## Frontend деплой

Frontend можно задеплоить на:
- Vercel (рекомендуется)
- Netlify
- Railway static site

Не забудьте обновить API URL в frontend/src/services/api.ts:
```typescript
const API_URL = 'https://your-railway-app.railway.app'
```
