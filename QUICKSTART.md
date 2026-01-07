# Быстрый старт

## Windows

### Автоматический запуск обоих серверов:
```bash
start_all.bat
```

### Или запустить отдельно:

Backend:
```bash
start_backend.bat
```

Frontend (в новом терминале):
```bash
start_frontend.bat
```

## Linux/Mac

### Backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend (в новом терминале):
```bash
cd frontend
npm install
npm run dev
```

## Важно!

Перед запуском создайте файл `.env` в папке `backend/`:
```env
OPENAI_API_KEY=your-openai-api-key-here
HUGGINGFACE_API_KEY=your-huggingface-key-here
```

Без OpenAI API ключа приложение будет работать с mock данными.
