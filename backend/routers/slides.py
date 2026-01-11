from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
import json
import os
from pathlib import Path

router = APIRouter()

DATA_DIR = Path(__file__).parent.parent / "data"

# Путь к файлам со слайдами (lang + deck)
SLIDES_FILES: Dict[str, Dict[str, Path]] = {
    "ky": {
        "default": DATA_DIR / "slides.json",
    },
    "ru": {
        "rights": DATA_DIR / "slides_ru.json",
        "mvd": DATA_DIR / "slides_ru_mvd.json",
        "default": DATA_DIR / "slides_ru.json",
    },
}


def _normalize_lang(lang: Optional[str]) -> str:
    normalized = (lang or "ky").strip().lower()
    return normalized if normalized in SLIDES_FILES else "ky"


def _normalize_deck(language: str, deck: Optional[str]) -> str:
    normalized = (deck or "default").strip().lower()
    if normalized in SLIDES_FILES[language]:
        return normalized

    # Backward compatible default behavior
    if language == "ru":
        return "rights"
    return "default"

def load_slides(lang: Optional[str] = None, deck: Optional[str] = None) -> List[Dict]:
    """Загрузить слайды из JSON файла"""
    try:
        language = _normalize_lang(lang)
        deck_name = _normalize_deck(language, deck)
        slides_file = SLIDES_FILES[language][deck_name]

        with open(slides_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("slides", [])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Slides file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing slides file")

@router.get("/slides")
async def get_all_slides(lang: Optional[str] = None, deck: Optional[str] = None):
    """Получить все слайды"""
    slides = load_slides(lang, deck)
    return {
        "total": len(slides),
        "slides": slides
    }

@router.get("/slides/{slide_id}")
async def get_slide(slide_id: int, lang: Optional[str] = None, deck: Optional[str] = None):
    """Получить конкретный слайд по ID"""
    slides = load_slides(lang, deck)
    
    if slide_id < 1 or slide_id > len(slides):
        raise HTTPException(status_code=404, detail=f"Slide {slide_id} not found")
    
    return slides[slide_id - 1]
