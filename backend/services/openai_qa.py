import os
from typing import Optional
import logging

try:
    import openai
except ImportError:
    openai = None

logger = logging.getLogger(__name__)

class OpenAIQA:
    """
    Сервис для ответов на вопросы через OpenAI GPT-4
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        if self.api_key and openai:
            openai.api_key = self.api_key
        self.model = "gpt-4"
    
    async def get_answer(
        self,
        question: str,
        context: str = "",
        slide_id: int = 0,
        language: str = "ky",
    ) -> str:
        """
        Получить ответ на вопрос с учетом контекста презентации
        
        Args:
            question: Вопрос пользователя
            context: Контекст текущего слайда
            slide_id: ID текущего слайда
            
        Returns:
            str: Ответ на языке презентации (ky или ru)
        """
        if not self.api_key or not openai:
            logger.warning("OPENAI_API_KEY not set, returning mock answer")
            if (language or "").strip().lower() == "ru":
                return "Это тестовый ответ. Укажите OPENAI_API_KEY. Вопрос: " + question
            return "Бул тест жообу. OpenAI API ачкычын коюңуз. Суроо: " + question
        
        lang = (language or "ky").strip().lower()

        # Системный промпт
        if lang == "ru":
            system_prompt = """Вы эксперт по правам человека.
    Отвечайте на русском языке чётко, понятно и кратко.
    Ответ должен опираться на контекст текущего слайда.
    Не более 3–4 предложений."""
        else:
            system_prompt = """Сиз адам укуктары боюнча эксперт экенсиз.
    Суроолорго кыргыз тилинде так, түшүнүктүү жана кыска жооп бериңиз.
    Жоопторуңуз презентациянын контекстине ылайык болсун.
    Жооптор 3-4 сүйлөмдөн ашпасын."""

        # Пользовательский промпт с контекстом
        if lang == "ru":
            user_prompt = f"""Слайд {slide_id} презентации:
    {context}

    Вопрос: {question}

    Ответ:"""
        else:
            user_prompt = f"""Презентациянын {slide_id}-слайды:
    {context}

    Суроо: {question}

    Жооп:"""

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            if lang == "ru":
                return f"Произошла ошибка при получении ответа: {str(e)}"
            return f"Жообун алууда катачылык болду: {str(e)}"
