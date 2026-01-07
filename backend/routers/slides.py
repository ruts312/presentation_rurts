from fastapi import APIRouter, HTTPException
from typing import List, Dict
import json
import os
from pathlib import Path

router = APIRouter()

# Путь к файлу со слайдами
SLIDES_FILE = Path(__file__).parent.parent / "data" / "slides.json"

def load_slides() -> List[Dict]:
    """Загрузить слайды из JSON файла"""
    try:
        with open(SLIDES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("slides", [])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Slides file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing slides file")

@router.get("/slides")
async def get_all_slides():
    """Получить все слайды"""
    slides = load_slides()
    return {
        "total": len(slides),
        "slides": slides
    }

@router.get("/slides/{slide_id}")
async def get_slide(slide_id: int):
    """Получить конкретный слайд по ID"""
    slides = load_slides()
    
    if slide_id < 1 or slide_id > len(slides):
        raise HTTPException(status_code=404, detail=f"Slide {slide_id} not found")
    
    return slides[slide_id - 1]
