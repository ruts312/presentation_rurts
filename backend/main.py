import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import slides, tts, stt, qa
import uvicorn
from dotenv import load_dotenv

# Загрузить переменные окружения
load_dotenv()

app = FastAPI(
    title="Кыргызская Презентация API",
    description="API для интерактивной презентации на кыргызском языке",
    version="1.0.0"
)

# Раздача готовых аудио-файлов слайдов
# backend/data/audio/slide_01.wav -> GET /audio/slide_01.wav
app.mount("/audio", StaticFiles(directory="data/audio"), name="audio")

# CORS настройки
# В проде на Railway удобнее задавать явно:
# - CORS_ALLOW_ORIGINS="https://<frontend-domain>" (через запятую для нескольких)
# или
# - CORS_ALLOW_ORIGIN_REGEX="https://.*\\.up\\.railway\\.app"
cors_allow_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
cors_allow_origin_regex = os.getenv("CORS_ALLOW_ORIGIN_REGEX", "").strip() or None

if cors_allow_origins_env:
    allow_origins = [o.strip() for o in cors_allow_origins_env.split(",") if o.strip()]
else:
    allow_origins = ["http://localhost:5173", "http://localhost:3000"]

# Если указан "*", браузеры запрещают allow_credentials=true — отключаем credentials.
allow_credentials = True
if any(o == "*" for o in allow_origins):
    allow_origins = ["*"]
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=cors_allow_origin_regex,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Подключение роутеров
app.include_router(slides.router, prefix="/api", tags=["slides"])
app.include_router(tts.router, prefix="/api", tags=["tts"])
app.include_router(stt.router, prefix="/api", tags=["stt"])
app.include_router(qa.router, prefix="/api", tags=["qa"])

@app.get("/")
async def root():
    return {
        "message": "Кыргызская Презентация API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
