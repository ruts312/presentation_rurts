from fastapi import APIRouter, UploadFile, File, HTTPException
from services.whisper_stt import WhisperSTT

router = APIRouter()
stt_service = WhisperSTT()

@router.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """
    Распознать речь из аудио файла
    Поддерживаемые форматы: wav, mp3, m4a, webm, ogg
    """
    try:
        # Проверка формата файла
        # В браузерах content-type может быть с параметрами (например: "audio/webm; codecs=opus")
        content_type_raw = (audio.content_type or "").strip().lower()
        content_type = content_type_raw.split(";", 1)[0].strip()

        allowed_formats = {
            "audio/wav",
            "audio/x-wav",
            "audio/mpeg",
            "audio/mp3",
            "audio/webm",
            "video/webm",
            "audio/ogg",
            "audio/x-m4a",
            "audio/mp4",
            "application/octet-stream",
        }

        if content_type not in allowed_formats:
            raise HTTPException(status_code=400, detail=f"Unsupported audio format: {audio.content_type}")

        # Чтение аудио файла
        audio_data = await audio.read()
        if not audio_data:
            raise HTTPException(status_code=400, detail="Empty audio")

        # Распознавание речи
        transcription = await stt_service.transcribe(audio_data, audio.filename)

        return {
            "text": transcription,
            "language": "ky",
            "filename": audio.filename,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT error: {str(e)}")

@router.get("/stt/test")
async def test_stt():
    """Тестовый эндпоинт для проверки STT"""
    return {
        "status": "ready",
        "service": "OpenAI Whisper",
        "supported_languages": ["ky", "ru", "en"]
    }
