"""
Генерация аудио для всех 25 слайдов
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from services.huggingface_tts import HuggingFaceTTS

load_dotenv()

# Make console output robust on Windows (avoid UnicodeEncodeError)
# Use getattr to keep static type checkers happy.
_stdout_reconfigure = getattr(sys.stdout, "reconfigure", None)
if callable(_stdout_reconfigure):
    _stdout_reconfigure(encoding="utf-8", errors="replace")

_stderr_reconfigure = getattr(sys.stderr, "reconfigure", None)
if callable(_stderr_reconfigure):
    _stderr_reconfigure(encoding="utf-8", errors="replace")

async def generate_all_slides():
    """Генерирует аудио для всех слайдов"""
    
    # Убедимся что используем OpenAI
    os.environ['USE_LOCAL_TTS'] = 'false'
    
    # Загрузить слайды
    with open('data/slides.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    slides = data['slides']
    
    # Создать папку для аудио
    audio_dir = Path('data/audio')
    audio_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print(f"Audio generation for {len(slides)} slides")
    print("Voice: onyx (OpenAI TTS HD)")
    print("=" * 80)
    print()
    
    # Инициализировать TTS
    tts = HuggingFaceTTS()
    
    for i, slide in enumerate(slides, 1):
        speak_text = slide.get('tts') or slide.get('content') or ''

        print(f"\n[{i}/{len(slides)}] {slide['title']}")
        print(f"   Длина текста: {len(speak_text)} символов")
        
        # Синтезировать
        try:
            audio_data = await tts.synthesize(speak_text, language='ky')
            
            # Сохранить
            slide_id = int(slide.get('id', i))
            filename = f"slide_{slide_id:02d}.wav"
            filepath = audio_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            
            size_kb = len(audio_data) / 1024
            print(f"   ✅ Сохранено: {filename} ({size_kb:.1f} KB)")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            continue
    
    print("\n" + "=" * 80)
    print("Generation finished")
    print(f"Files saved to: {audio_dir.absolute()}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(generate_all_slides())
