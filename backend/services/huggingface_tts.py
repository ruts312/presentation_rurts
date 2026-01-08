import os
import asyncio
from typing import Optional
import logging
import struct
import wave
import io

# Импорты для OpenAI TTS
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Импорты для локальных моделей
try:
    import torch
    from transformers import pipeline
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)

class HuggingFaceTTS:
    """
    Сервис для синтеза речи - OpenAI API или локальные модели
    """
    
    def __init__(self):
        self.use_local = os.getenv("USE_LOCAL_TTS", "false").lower() == "true"
        
        if self.use_local:
            # Локальная модель
            self.model_name = os.getenv("HUGGINGFACE_TTS_MODEL", "seprised/my-voice-ky-raw")
            self.synthesizer = None
            
            if TORCH_AVAILABLE:
                try:
                    logger.info(f"Loading local TTS model: {self.model_name}")
                    self.synthesizer = pipeline(
                        "text-to-speech",
                        model=self.model_name,
                        device=0 if torch.cuda.is_available() else -1
                    )
                    logger.info("✅ Local TTS model loaded successfully")
                except Exception as e:
                    logger.error(f"Failed to load local TTS model: {e}")
                    self.synthesizer = None
            else:
                logger.warning("torch not available for local TTS")
        else:
            # OpenAI API
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
        if self.use_local:
            # Локальный синтез
            return await self._synthesize_local(text)
        else:
            # OpenAI API
            return await self._synthesize_openai(text)
    
    async def _synthesize_local(self, text: str) -> bytes:
        """Локальный синтез через HuggingFace модель"""
        if not self.synthesizer:
            logger.warning("Local TTS model not available, using mock audio")
            return self._generate_mock_audio()
        
        try:
            logger.info(f"Synthesizing with local model: {text[:100]}...")
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.synthesizer(text)
            )
            
            audio_bytes = self._convert_to_wav(result)
            logger.info(f"Successfully generated audio, size: {len(audio_bytes)} bytes")
            return audio_bytes
                
        except Exception as e:
            logger.error(f"Local TTS error: {str(e)}")
            return self._generate_mock_audio()
    
    async def _synthesize_openai(self, text: str) -> bytes:
        """Синтез через OpenAI TTS API"""
        if not hasattr(self, 'client') or not self.client:
            logger.warning("OpenAI TTS not available, using mock audio")
            return self._generate_mock_audio()
        
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
            return self._generate_mock_audio()
    
    def _convert_to_wav(self, result) -> bytes:
        """Конвертировать результат локальной модели в WAV"""
        try:
            import numpy as np
            
            if isinstance(result, dict):
                audio_array = result.get("audio")
                sample_rate = result.get("sampling_rate") or result.get("sample_rate", 22050)
            elif hasattr(result, 'audio'):
                audio_array = result.audio
                sample_rate = getattr(result, 'sampling_rate', None) or getattr(result, 'sample_rate', 22050)
            else:
                audio_array = result
                sample_rate = 22050
            
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                
                if isinstance(audio_array, np.ndarray):
                    if audio_array.dtype in [np.float32, np.float64]:
                        audio_array = np.clip(audio_array, -1.0, 1.0)
                        audio_int16 = (audio_array * 32767).astype(np.int16)
                    else:
                        audio_int16 = audio_array.astype(np.int16)
                else:
                    audio_array = np.array(audio_array)
                    audio_array = np.clip(audio_array, -1.0, 1.0)
                    audio_int16 = (audio_array * 32767).astype(np.int16)
                
                wav_file.writeframes(audio_int16.tobytes())
            
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._generate_mock_audio()
    
    
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

