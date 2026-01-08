"""
Тест разных голосов OpenAI TTS для кыргызского текста
"""
import asyncio
import json
import os
from dotenv import load_dotenv
from services.huggingface_tts import HuggingFaceTTS

load_dotenv()

async def test_all_voices():
    """Тестирует все доступные голоса"""
    
    # Короткий тестовый текст
    test_text = "Саламатсызбы! Адам укуктары – бул ар бир адамдын туулгандан тартып ээ болгон негизги укуктары."
    
    print("🎤 Генерация аудио для разных голосов...")
    print()
    
    # Доступные голоса
    voices = {
        'alloy': 'Нейтральный (alloy)',
        'echo': 'Мужской (echo)', 
        'fable': 'Британский акцент (fable)',
        'onyx': 'Глубокий мужской (onyx)',
        'nova': 'Женский энергичный (nova)',
        'shimmer': 'Женский мягкий (shimmer)'
    }
    
    models = ['tts-1', 'tts-1-hd']
    
    for model in models:
        print(f"\n{'='*60}")
        print(f"📊 Модель: {model}")
        print(f"{'='*60}\n")
        
        for voice_id, voice_desc in voices.items():
            print(f"🔊 Голос: {voice_desc}")
            
            # Установить переменные окружения
            os.environ['TTS_MODEL'] = model
            os.environ['TTS_VOICE'] = voice_id
            
            # Инициализировать TTS
            tts = HuggingFaceTTS()
            
            # Синтезировать
            audio_data = await tts.synthesize(test_text, language='ky')
            
            # Сохранить файл
            filename = f"test_voice_{model}_{voice_id}.wav"
            filepath = os.path.join(os.path.dirname(__file__), filename)
            
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            
            print(f"   ✅ Сохранено: {filename} ({len(audio_data)} байт)")
            print()
    
    print("\n" + "="*60)
    print("✨ Все голоса сгенерированы!")
    print("="*60)
    print("\n🎧 Прослушайте файлы и выберите лучший голос:")
    print()
    for model in models:
        for voice_id, voice_desc in voices.items():
            print(f"   - test_voice_{model}_{voice_id}.wav ({voice_desc})")
    print()

if __name__ == "__main__":
    asyncio.run(test_all_voices())
