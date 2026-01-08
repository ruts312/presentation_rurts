"""Legacy compatibility module.

The project now uses OpenAI-only TTS. This module remains to avoid breaking
older imports, but it no longer depends on Hugging Face libraries.
"""

from .huggingface_tts import HuggingFaceTTS

__all__ = ["HuggingFaceTTS"]
