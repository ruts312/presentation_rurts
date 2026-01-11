import os
import asyncio
import logging
import struct
import wave
import io
import tempfile
from typing import Optional

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

logger = logging.getLogger(__name__)

class HuggingFaceTTS:
    """
    Сервис для синтеза речи через OpenAI TTS.

    Исторически класс назывался HuggingFaceTTS, поэтому имя сохранено,
    чтобы не ломать импорты в роутерах.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.voice = os.getenv("TTS_VOICE", "onyx")
        self.model = os.getenv("TTS_MODEL", "tts-1-hd")

        if self.api_key and OPENAI_AVAILABLE:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info(f"✅ OpenAI TTS initialized (model: {self.model}, voice: {self.voice})")
        else:
            self.client = None
            logger.warning("OpenAI TTS not available")
        
    async def synthesize(self, text: str, language: str = "ky") -> bytes:
        """
        Синтез речи из текста
        
        Args:
            text: Текст для озвучки
            language: Код языка
            
        Returns:
            bytes: Аудио данные в формате WAV
        """
        _ = language
        return await self._synthesize_openai(text)
    
    async def _synthesize_openai(self, text: str) -> bytes:
        """Синтез через OpenAI TTS API"""
        if not hasattr(self, 'client') or not self.client:
            logger.warning("OpenAI TTS not available, using mock audio")
            local = await self._try_synthesize_local(text)
            return local if local else self._generate_mock_audio()
        
        try:
            logger.info(f"Synthesizing with OpenAI TTS: {text[:100]}...")
            
            response = await self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text,
                response_format="wav"
            )
            
            audio_bytes = response.content
            logger.info(f"Successfully generated audio, size: {len(audio_bytes)} bytes")
            return audio_bytes
                
        except Exception as e:
            logger.error(f"OpenAI TTS error: {str(e)}")
            local = await self._try_synthesize_local(text)
            return local if local else self._generate_mock_audio()


    async def _try_synthesize_local(self, text: str) -> Optional[bytes]:
        """Best-effort local TTS (Windows SAPI via pyttsx3) to avoid silence files."""
        if not PYTTSX3_AVAILABLE:
            return None

        try:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, self._synthesize_pyttsx3_sync, text)
        except Exception as e:
            logger.warning(f"Local TTS fallback failed: {e}")
            return None


    def _synthesize_pyttsx3_sync(self, text: str) -> bytes:
        engine = pyttsx3.init()

        # Try to pick a Russian voice if available, otherwise keep default.
        try:
            voices = engine.getProperty('voices') or []
            preferred = None
            for v in voices:
                desc = " ".join(
                    [
                        str(getattr(v, 'id', '')),
                        str(getattr(v, 'name', '')),
                        str(getattr(v, 'languages', '')),
                    ]
                ).lower()
                if any(k in desc for k in ["ru", "russian", "ирина", "irina"]):
                    preferred = v
                    break
            if preferred is not None:
                engine.setProperty('voice', preferred.id)
        except Exception:
            pass

        # Slightly faster speaking rate (optional)
        try:
            rate = engine.getProperty('rate')
            engine.setProperty('rate', int(rate * 1.05))
        except Exception:
            pass

        tmp_path = None
        try:
            fd, tmp_path = tempfile.mkstemp(suffix='.wav')
            os.close(fd)

            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            engine.stop()

            with open(tmp_path, 'rb') as f:
                return f.read()
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
    
    
    def _generate_mock_audio(self) -> bytes:
        """
        Генерация заглушки аудио (1 секунда тишины)
        """
        logger.info("Generating mock audio (silence)")
        
        # Параметры аудио
        sample_rate = 22050
        duration = 1.0
        num_samples = int(sample_rate * duration)
        
        # Создать WAV файл в памяти
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Моно
            wav_file.setsampwidth(2)   # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Записать тишину (нули)
            silence = struct.pack('<' + 'h' * num_samples, *([0] * num_samples))
            wav_file.writeframes(silence)
        
        return buffer.getvalue()

