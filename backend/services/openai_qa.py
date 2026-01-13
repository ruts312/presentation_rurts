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
        # Newer + cheaper default model; can be overridden with QA_MODEL.
        # Examples: gpt-4o-mini (cheap), gpt-4o (stronger), etc.
        self.model = os.getenv("QA_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
        self.allow_general = os.getenv("QA_ALLOW_GENERAL", "true").strip().lower() in {"1", "true", "yes", "y", "on"}

    def _maybe_fact_override(self, question: str, language: str) -> Optional[str]:
        q = (question or "").strip().lower()
        lang = (language or "ky").strip().lower()

        # Конституция Кыргызской Республики: действующая редакция вступила в силу 5 мая 2021.
        # Делается явным «фактовым» оверрайдом, чтобы не выдавать устаревшие даты.
        is_kr = any(k in q for k in [
            "кыргыз", "киргиз", "кыргызстан", "кыргызской республики", "кыргыз республика", "кр",
        ])
        is_constitution = any(k in q for k in ["конституц", "конституция"])
        asks_date = any(k in q for k in [
            "когда", "дата", "принят", "принята", "вступил", "вступила", "вступление", "последн", "актуальн", "редакц",
        ])

        if is_kr and is_constitution and asks_date:
            if lang == "ru":
                return "Действующая Конституция Кыргызской Республики вступила в силу 5 мая 2021 года."
            return "Кыргыз Республикасынын Конституциясынын азыркы редакциясы 2021-жылдын 5-майында күчүнө кирген."

        return None
    
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
        override = self._maybe_fact_override(question=question, language=language)
        if override:
            return override

        if not self.api_key or not openai:
            logger.warning("OPENAI_API_KEY not set, returning mock answer")
            if (language or "").strip().lower() == "ru":
                return "Это тестовый ответ. Укажите OPENAI_API_KEY. Вопрос: " + question
            return "Бул тест жообу. OpenAI API ачкычын коюңуз. Суроо: " + question
        
        lang = (language or "ky").strip().lower()

        allow_general = self.allow_general

        # Системный промпт
        if lang == "ru":
            system_prompt = """Вы эксперт-ассистент.
Отвечайте на русском языке чётко, понятно и кратко (обычно 1–4 предложения).

Проверенные факты (используйте как опорные):
- Действующая Конституция Кыргызской Республики вступила в силу 5 мая 2021 года.

Если дан дополнительный контекст, используйте его как вспомогательный источник.
Никогда не упоминайте «презентацию», «слайды», «в презентации нет/не указано» и не оправдывайтесь отсутствием информации.
""" + ("Если контекст недостаточен, всё равно отвечайте по сути, опираясь на общие знания. Если уверенности нет — прямо скажите, что не уверены, и кратко уточните." if allow_general else "Если контекст недостаточен — скажите, что данных недостаточно, и задайте 1 уточняющий вопрос.")
        else:
            system_prompt = """Сиз эксперт-ассистентсиз.
Суроолорго кыргыз тилинде так, түшүнүктүү жана кыска жооп бериңиз (адатта 1–4 сүйлөм).

Текшерилген фактылар (таянуу үчүн):
- Кыргыз Республикасынын Конституциясынын азыркы редакциясы 2021-жылдын 5-майында күчүнө кирген.

Эгер кошумча контекст берилсе, аны жардамчы булак катары колдонуңуз.
Эч качан «презентация», «слайд» же «презентацияда маалымат жок/көрсөтүлгөн эмес» деген сөздөрдү айтпаңыз.
""" + ("Эгер контекст жетишсиз болсо да, жалпы билимге таянып түз жооп бериңиз. Эгер ишеним жок болсо — кыскача ишенбестигиңизди айтыңыз жана тактоо үчүн 1 суроо бериңиз." if allow_general else "Эгер контекст жетишсиз болсо — маалымат жетишсиз экенин айтыңыз жана 1 тактоочу суроо бериңиз.")

        # Пользовательский промпт с контекстом
        if lang == "ru":
            user_prompt = f"""Контекст (может быть пустым):
{context}

Вопрос: {question}

Ответ:"""
        else:
            user_prompt = f"""Контекст (бош болушу мүмкүн):
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
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            if lang == "ru":
                return f"Произошла ошибка при получении ответа: {str(e)}"
            return f"Жообун алууда катачылык болду: {str(e)}"
