from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
