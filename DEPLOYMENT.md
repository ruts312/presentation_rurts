# 🌐 Развертывание в Production

## Варианты развертывания

### 1. Vercel (Frontend) + Railway/Render (Backend)

#### Frontend на Vercel

```bash
cd frontend

# Установить Vercel CLI
npm i -g vercel

# Развернуть
vercel
```

Настройки в Vercel:
- Build Command: `npm run build`
- Output Directory: `dist`
- Environment Variables: `VITE_API_URL=https://your-backend.railway.app/api`

#### Backend на Railway

1. Зарегистрируйтесь на https://railway.app
2. Создайте новый проект
3. Подключите GitHub репозиторий
4. Установите переменные окружения:
   - `OPENAI_API_KEY`
   - `HUGGINGFACE_API_KEY`
5. Railway автоматически определит Python и развернет

### 2. Docker (рекомендуется)

#### Backend Dockerfile

Создайте `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile

Создайте `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### docker-compose.yml

Создайте в корне проекта:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

Запуск:
```bash
docker-compose up -d
```

### 3. AWS (Production-ready)

#### Backend на AWS Lambda + API Gateway

1. Установите Serverless Framework:
```bash
npm install -g serverless
```

2. Создайте `backend/serverless.yml`:
```yaml
service: presentation-backend

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  environment:
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}
    HUGGINGFACE_API_KEY: ${env:HUGGINGFACE_API_KEY}

functions:
  api:
    handler: main.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
```

3. Адаптируйте `main.py` для Lambda:
```python
from mangum import Mangum

# ... существующий код ...

handler = Mangum(app)
```

#### Frontend на AWS S3 + CloudFront

```bash
cd frontend
npm run build

# Загрузите dist/ в S3 bucket
aws s3 sync dist/ s3://your-bucket-name --acl public-read

# Создайте CloudFront distribution для HTTPS
```

### 4. Digital Ocean App Platform

1. Создайте аккаунт на https://www.digitalocean.com
2. Выберите "App Platform"
3. Подключите GitHub репозиторий
4. Настройте компоненты:

**Backend:**
- Type: Web Service
- Source: `backend/`
- Run Command: `uvicorn main:app --host 0.0.0.0 --port 8080`
- Environment Variables: добавьте API ключи

**Frontend:**
- Type: Static Site
- Source: `frontend/`
- Build Command: `npm run build`
- Output Directory: `dist`

## 🔒 Production Checklist

### Backend

- [ ] Установить `python-decouple` для безопасности
- [ ] Настроить CORS только для production домена
- [ ] Добавить rate limiting
- [ ] Настроить логирование (Sentry, LogRocket)
- [ ] Использовать gunicorn + uvicorn workers
- [ ] Настроить HTTPS (Let's Encrypt)
- [ ] Добавить health checks
- [ ] Настроить мониторинг (Prometheus, Grafana)

### Frontend

- [ ] Минифицировать и оптимизировать build
- [ ] Настроить CDN для статики
- [ ] Включить gzip compression
- [ ] Добавить Service Worker для кеширования
- [ ] Настроить error tracking (Sentry)
- [ ] Оптимизировать изображения
- [ ] Настроить analytics (Google Analytics)

### Безопасность

- [ ] Использовать HTTPS везде
- [ ] Настроить CSP headers
- [ ] Защитить от XSS
- [ ] Ограничить размер загружаемых файлов
- [ ] Валидировать все входные данные
- [ ] Использовать secrets management (AWS Secrets Manager)
- [ ] Настроить WAF (Web Application Firewall)

### Производительность

- [ ] Кеширование API ответов
- [ ] Использовать CDN
- [ ] Оптимизировать базу данных (если добавите)
- [ ] Настроить load balancing
- [ ] Использовать Redis для кеша
- [ ] Оптимизировать bundle size

## 📊 Мониторинг

### Рекомендуемые инструменты:

1. **Uptime monitoring**: UptimeRobot, Pingdom
2. **Error tracking**: Sentry
3. **Analytics**: Google Analytics, Plausible
4. **Performance**: New Relic, DataDog
5. **Logs**: CloudWatch, Papertrail

### Метрики для отслеживания:

- Uptime (должно быть > 99.9%)
- Response time (< 200ms для API)
- Error rate (< 0.1%)
- API usage (для контроля расходов)
- User sessions
- Page load time

## 💸 Оптимизация расходов

### OpenAI API

1. Кешируйте частые вопросы
2. Ограничьте длину ответов
3. Используйте GPT-3.5-turbo для простых вопросов
4. Установите rate limits

### Хостинг

1. Используйте auto-scaling только при необходимости
2. Выбирайте подходящий instance type
3. Используйте spot instances для non-critical workloads
4. Мониторьте использование ресурсов

## 🔄 CI/CD Pipeline

### GitHub Actions example

Создайте `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest
      
      - name: Deploy to production
        run: |
          # Your deployment script
          
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      
      - name: Install and build
        run: |
          cd frontend
          npm ci
          npm run build
      
      - name: Deploy to production
        run: |
          # Your deployment script
```

## 🌍 Масштабирование

### Horizontal Scaling

1. Используйте load balancer (AWS ALB, Nginx)
2. Запустите несколько инстансов backend
3. Используйте shared state (Redis, database)

### Vertical Scaling

1. Увеличьте ресурсы сервера
2. Оптимизируйте код
3. Используйте профилирование

### Database (если добавите)

1. PostgreSQL для реляционных данных
2. Redis для кеширования
3. S3 для медиа файлов
4. Регулярные бэкапы

## 📝 Environment Variables Production

```env
# Backend Production
OPENAI_API_KEY=sk-prod-xxx
HUGGINGFACE_API_KEY=hf_prod-xxx
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://host:6379
SENTRY_DSN=https://xxx@sentry.io/xxx
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com

# Frontend Production
VITE_API_URL=https://api.yourdomain.com
VITE_GA_ID=UA-XXXXX-Y
VITE_SENTRY_DSN=https://xxx@sentry.io/xxx
```

## 🚀 Deployment Commands

### Vercel
```bash
vercel --prod
```

### Railway
```bash
railway up
```

### Heroku
```bash
git push heroku main
```

### AWS
```bash
serverless deploy --stage production
```

### Docker
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

Выберите подходящий вариант развертывания в зависимости от ваших требований и бюджета!
