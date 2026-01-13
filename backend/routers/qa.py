from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.openai_qa import OpenAIQA
from services.huggingface_tts import HuggingFaceTTS
from fastapi.responses import JSONResponse
import base64

router = APIRouter()
qa_service = OpenAIQA()
tts_service = HuggingFaceTTS()

class QARequest(BaseModel):
    question: str
    slide_context: str = ""
    slide_id: int = 0
    language: str = "ru"

@router.post("/qa")
async def question_answer(request: QARequest):
    """
    Обработать вопрос пользователя и вернуть ответ с озвучкой
    """
    try:
        # Получение ответа от GPT-4
        answer_text = await qa_service.get_answer(
            question=request.question,
            context=request.slide_context,
            slide_id=request.slide_id,
            language=request.language,
        )
        
        # Озвучка ответа
        audio_data = await tts_service.synthesize(answer_text, request.language)
        
        # Конвертация аудио в base64 для передачи в JSON
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return {
            "question": request.question,
            "answer": answer_text,
            "audio": audio_base64,
            "audio_format": "wav"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QA error: {str(e)}")

@router.get("/qa/test")
async def test_qa():
    """Тестовый эндпоинт для проверки QA сервиса"""
    return {
        "status": "ready",
        "service": "OpenAI Chat (configurable via QA_MODEL)",
        "features": ["question_answering", "context_aware", "ru_default", "kyrgyz_supported"]
    }
