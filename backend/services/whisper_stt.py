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
            # Важно: Whisper API не поддерживает language="ky" (Kyrgyz) и вернёт 400.
            # Поэтому для кыргызского используем авто-определение языка (не передаём параметр language).
            language_hint_raw = (os.getenv("STT_LANGUAGE", "ky") or "").strip().lower()
            language_hint: Optional[str] = language_hint_raw if language_hint_raw and language_hint_raw not in {"ky", "kyrgyz", "kirghiz"} else None

            with open(temp_path, "rb") as audio_file:
                params = {
                    "model": "whisper-1",
                    "file": audio_file,
                }
                if language_hint:
                    params["language"] = language_hint

                try:
                    transcript = client.audio.transcriptions.create(**params)
                except Exception as e:
                    # Если язык не поддерживается (часто это происходит для ky) — пробуем ещё раз без language
                    msg = str(e)
                    if ("unsupported_language" in msg) or ("Language 'ky' is not supported" in msg):
                        params.pop("language", None)
                        transcript = client.audio.transcriptions.create(**params)
                    else:
                        raise
            
            # Удаление временного файла
            os.unlink(temp_path)
            
            return transcript.text
            
        except Exception as e:
            # Важно: не маскируем причину ошибки, иначе на фронте всегда будет
            # одно и то же сообщение и невозможно понять, что именно сломалось
            # (ключ/квота/формат/лимиты/сеть).
            logger.exception("Whisper transcription error")

            # Не включаем секреты; как правило, сообщения SDK не содержат ключ.
            err_type = type(e).__name__
            err_msg = str(e).strip() or "Unknown error"
            raise RuntimeError(f"Speech recognition failed ({err_type}): {err_msg}") from e
