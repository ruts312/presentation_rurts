import os
import asyncio
from typing import Optional
import logging
from huggingface_hub import InferenceClient
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class HuggingFaceTTS:
    """
    Сервис для синтеза речи на кыргызском языке через Hugging Face Inference API
    """
    
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        # Модель для кыргызского TTS
        self.model = os.getenv("HUGGINGFACE_TTS_MODEL", "kyrgyz-ai/TTS_small")
        # Используем InferenceClient для TTS
        if self.api_key:
            self.client = InferenceClient(token=self.api_key)
        else:
            self.client = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        logger.info(f"Using TTS model: {self.model}")
        
    async def synthesize(self, text: str, language: str = "ky") -> bytes:
        """
        Синтез речи из текста
        
        Args:
            text: Текст для озвучки
            language: Код языка (ky - кыргызский)
            
        Returns:
            bytes: Аудио данные в формате WAV
        """
        if not self.api_key or not self.client:
            logger.warning("HUGGINGFACE_API_KEY not set, using mock audio")
            return self._generate_mock_audio()
        
        try:
            logger.info(f"Sending request to model: {self.model}")
            logger.info(f"Input text: {text[:100]}...")
            
            # Используем ThreadPoolExecutor для избежания StopIteration проблемы
            loop = asyncio.get_event_loop()
            audio_bytes = await loop.run_in_executor(
                self.executor,
                lambda: self.client.text_to_speech(text, model=self.model)
            )
            
            logger.info(f"Successfully generated audio, size: {len(audio_bytes)} bytes")
            return audio_bytes
                
        except Exception as e:
            logger.error(f"HuggingFace TTS error: {str(e)}")
            return self._generate_mock_audio()
    
    def _generate_mock_audio(self) -> bytes:
        """
        Генерация заглушки для аудио (для тестирования без API ключа)
        Простой WAV файл с тишиной
        """
        import struct
        import wave
        import io
        
        # Параметры WAV
        sample_rate = 22050
        duration = 2  # секунды
        num_samples = sample_rate * duration
        
        # Создание WAV в памяти
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # моно
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Генерация тишины
            for _ in range(num_samples):
                wav_file.writeframes(struct.pack('<h', 0))
        
        buffer.seek(0)
        return buffer.read()
