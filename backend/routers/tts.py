from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.huggingface_tts import HuggingFaceTTS
from services.cache import cache_service
import io

router = APIRouter()
tts_service = HuggingFaceTTS()

class TTSRequest(BaseModel):
    text: str
    language: str = "ky"  # Кыргызский язык

@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Преобразовать текст в речь (кыргызский язык)
    """
    try:
        # Проверить кеш
        cached_audio = cache_service.get_tts_cache(request.text, request.language)
        if cached_audio:
            return StreamingResponse(
                io.BytesIO(cached_audio),
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "inline; filename=speech.wav",
                    "X-Cache": "HIT"
                }
            )
        
        # Генерация аудио
        audio_data = await tts_service.synthesize(request.text, request.language)
        
        # Сохранить в кеш
        cache_service.set_tts_cache(request.text, audio_data, request.language)
        
        # Возврат аудио как streaming response
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=speech.wav",
                "X-Cache": "MISS"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

@router.get("/tts/test")
async def test_tts():
    """Тестовый эндпоинт для проверки TTS"""
    return {
        "status": "ready",
        "service": "HuggingFace TTS",
        "language": "Kyrgyz"
    }
