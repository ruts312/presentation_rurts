import os
from typing import Optional
import logging
import tempfile

try:
    import openai
except ImportError:
    openai = None

logger = logging.getLogger(__name__)

class WhisperSTT:
    """
    Сервис для распознавания речи через OpenAI Whisper API
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        if self.api_key and openai:
            openai.api_key = self.api_key
    
    async def transcribe(self, audio_data: bytes, filename: str = "audio.wav") -> str:
        """
        Распознать речь из аудио
        
        Args:
            audio_data: Аудио данные в байтах
            filename: Имя файла (для определения формата)
            
        Returns:
            str: Распознанный текст
        """
        if not self.api_key or not openai:
            logger.warning("OPENAI_API_KEY not set, returning mock transcription")
            return "Бул тест транскрипциясы. API ачкычын коюңуз."
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            # Сохранение аудио во временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Распознавание через Whisper API
            with open(temp_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ky"  # Кыргызский язык
                )
            
            # Удаление временного файла
            os.unlink(temp_path)
            
            return transcript.text
            
        except Exception as e:
            logger.error(f"Whisper transcription error: {str(e)}")
            # В случае ошибки возвращаем заглушку
            return "Суроону угууда катачылык болду. Кайра аракет кылып көрүңүз."
