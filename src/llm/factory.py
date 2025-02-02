from typing import Optional
from ..config.settings import Settings
from .base import BaseLLMProvider, LLMException
from .openai import OpenAIProvider
from .ollama import OllamaProvider

def create_llm_provider(settings: Settings) -> BaseLLMProvider:
    """Create LLM provider instance based on configuration"""
    provider_name = settings.LLM_PROVIDER.lower()

    if provider_name == "openai":
        return OpenAIProvider(settings)
    elif provider_name == "ollama":
        return OllamaProvider(settings)
    else:
        raise LLMException(f"Unsupported LLM provider: {provider_name}")

__all__ = ["create_llm_provider"]