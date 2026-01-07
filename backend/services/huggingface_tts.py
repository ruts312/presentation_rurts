import os
import httpx
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class HuggingFaceTTS:
    """
    Сервис для синтеза речи на кыргызском языке через Hugging Face Inference API
    """
    
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        # Модель для кыргызского TTS (если нет специализированной, используем многоязычную)
        # Можно использовать: facebook/mms-tts-kir или другую модель
        self.model = os.getenv("HUGGINGFACE_TTS_MODEL", "facebook/mms-tts-rus")
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        
    async def synthesize(self, text: str, language: str = "ky") -> bytes:
        """
        Синтез речи из текста
        
        Args:
            text: Текст для озвучки
            language: Код языка (ky - кыргызский)
            
        Returns:
            bytes: Аудио данные в формате WAV
        """
        if not self.api_key:
            logger.warning("HUGGINGFACE_API_KEY not set, using mock audio")
            return self._generate_mock_audio()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": text
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    return response.content
                elif response.status_code == 503:
                    # Модель загружается, повторная попытка
                    logger.info("Model is loading, retrying...")
                    await asyncio.sleep(5)
                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=payload
                    )
                    if response.status_code == 200:
                        return response.content
                
                logger.error(f"HuggingFace API error: {response.status_code} - {response.text}")
                return self._generate_mock_audio()
                
        except Exception as e:
            logger.error(f"TTS synthesis error: {str(e)}")
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
