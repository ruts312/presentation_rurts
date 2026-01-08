"""
Тестовый скрипт для озвучивания первого слайда
"""
import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from services.huggingface_tts import HuggingFaceTTS

# Загрузить .env файл
load_dotenv()

async def test_first_slide():
    # Проверить API ключ
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    print(f"🔑 API ключ: {'✅ Установлен' if api_key else '❌ Не найден'}")
    if api_key:
        print(f"   Начало: {api_key[:10]}...")
    print()
    
    # Загрузить слайды
    slides_file = Path(__file__).parent / "data" / "slides.json"
    with open(slides_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        first_slide = data["slides"][0]
    
    print(f"📝 Слайд: {first_slide['title']}")
    print(f"📄 Контент: {first_slide['content'][:100]}...")
    print()
    
    # Инициализировать TTS
    tts = HuggingFaceTTS()
    
    print("🎤 Начинаю синтез речи...")
    if tts.use_local:
        print(f"🤖 Локальная модель: {tts.model_name}")
    else:
        print(f"🤖 OpenAI - Модель: {tts.model}, Голос: {tts.voice}")
    print()
    
    # Синтезировать речь
    audio_data = await tts.synthesize(first_slide['content'], language='ky')
    
    # Сохранить аудио
    output_file = Path(__file__).parent / "test_slide_1_audio.wav"
    with open(output_file, "wb") as f:
        f.write(audio_data)
    
    print(f"✅ Аудио сохранено: {output_file}")
    print(f"📊 Размер: {len(audio_data)} байт")
    print()
    print("🎧 Откройте файл test_slide_1_audio.wav для прослушивания")

if __name__ == "__main__":
    asyncio.run(test_first_slide())
