import redis
import os
import hashlib
import json
from typing import Optional, Union, cast

class CacheService:
    def __init__(self):
        # Попытка подключения к Redis, но не критично если не установлен
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = False
        
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=False,
                socket_connect_timeout=2
            )
            # Проверка подключения
            self.redis_client.ping()
            self.enabled = True
            print("✅ Redis кеш активирован")
        except Exception as e:
            self.redis_client = None
            self.enabled = False
            print(f"⚠️ Redis не доступен, кеширование отключено: {e}")

    def _get_key(self, prefix: str, data: str) -> str:
        """Создать ключ для кеша"""
        hash_obj = hashlib.md5(data.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"

    def get_tts_cache(self, text: str, language: str = 'ky') -> Optional[bytes]:
        """Получить кешированный TTS аудио"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            key = self._get_key('tts', f"{language}:{text}")
            cached = self.redis_client.get(key)
            if cached:
                print(f"✅ TTS кеш найден для: {text[:50]}...")
                return cast(bytes, cached)
            return None
        except Exception as e:
            print(f"Ошибка чтения TTS кеша: {e}")
            return None

    def set_tts_cache(self, text: str, audio_data: bytes, language: str = 'ky', ttl: int = 86400):
        """Сохранить TTS аудио в кеш"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            key = self._get_key('tts', f"{language}:{text}")
            self.redis_client.setex(key, ttl, audio_data)
            print(f"✅ TTS сохранен в кеш: {text[:50]}...")
        except Exception as e:
            print(f"Ошибка записи TTS кеша: {e}")

    def get_qa_cache(self, question: str, slide_id: int) -> Optional[dict]:
        """Получить кешированный ответ на вопрос"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            key = self._get_key('qa', f"{slide_id}:{question}")
            cached = self.redis_client.get(key)
            if cached:
                print(f"✅ QA кеш найден для вопроса: {question[:50]}...")
                cached_bytes = cast(bytes, cached)
                return json.loads(cached_bytes.decode('utf-8'))
            return None
        except Exception as e:
            print(f"Ошибка чтения QA кеша: {e}")
            return None

    def set_qa_cache(self, question: str, slide_id: int, answer: dict, ttl: int = 3600):
        """Сохранить ответ на вопрос в кеш"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            key = self._get_key('qa', f"{slide_id}:{question}")
            self.redis_client.setex(key, ttl, json.dumps(answer))
            print(f"✅ QA ответ сохранен в кеш")
        except Exception as e:
            print(f"Ошибка записи QA кеша: {e}")

    def clear_cache(self, pattern: str = "*"):
        """Очистить кеш по шаблону"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            keys_result = self.redis_client.keys(pattern)
            keys = cast(list, keys_result)
            if keys:
                self.redis_client.delete(*keys)
                print(f"✅ Очищено {len(keys)} ключей из кеша")
        except Exception as e:
            print(f"Ошибка очистки кеша: {e}")

# Создать глобальный экземпляр
cache_service = CacheService()
