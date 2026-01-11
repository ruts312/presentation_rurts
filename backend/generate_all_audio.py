"""generate_all_audio.py

Генерация озвучки слайдов.

По умолчанию сохраняет кыргызскую озвучку как раньше:
    backend/data/audio/slide_01.wav

Для русской версии сохраняет отдельным набором, чтобы не перезаписывать:
    backend/data/audio/ru/slide_01.wav

Для русской презентации про МВД:
    backend/data/audio/ru/mvd/slide_01.wav
"""
import asyncio
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional
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

def _resolve_paths(lang: str, deck: Optional[str] = None) -> tuple[Path, Path, str]:
    language = (lang or "ky").strip().lower()
    if language == "ru":
        normalized_deck = (deck or "rights").strip().lower()
        if normalized_deck == "mvd":
            slides_file = Path("data") / "slides_ru_mvd.json"
            audio_dir = Path("data") / "audio" / "ru" / "mvd"
            return slides_file, audio_dir, "ru"

        slides_file = Path("data") / "slides_ru.json"
        audio_dir = Path("data") / "audio" / "ru"
        return slides_file, audio_dir, "ru"

    slides_file = Path("data") / "slides.json"
    audio_dir = Path("data") / "audio"
    return slides_file, audio_dir, "ky"


async def generate_all_slides(lang: str = "ky", deck: Optional[str] = None):
    """Генерирует аудио для всех слайдов выбранного языка"""
    
    # Убедимся что используем OpenAI
    os.environ['USE_LOCAL_TTS'] = 'false'
    
    slides_file, audio_dir, language = _resolve_paths(lang, deck)

    # Загрузить слайды
    with open(slides_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    slides = data['slides']
    
    # Создать папку для аудио
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print(f"Audio generation for {len(slides)} slides (lang={language})")
    print(f"Voice: {os.getenv('TTS_VOICE', 'onyx')} (OpenAI TTS)")
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
            audio_data = await tts.synthesize(speak_text, language=language)
            
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
    parser = argparse.ArgumentParser(description="Generate slide audio")
    parser.add_argument("--lang", default="ky", choices=["ky", "ru"], help="Language to generate")
    parser.add_argument("--deck", default=None, choices=["rights", "mvd"], help="Deck for ru (optional)")
    parser.add_argument("--both", action="store_true", help="Generate for both ky and ru")
    args = parser.parse_args()

    if args.both:
        asyncio.run(generate_all_slides("ky"))
        asyncio.run(generate_all_slides("ru", args.deck))
    else:
        asyncio.run(generate_all_slides(args.lang, args.deck))
