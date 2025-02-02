from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseLLMProvider, LLMResponse, LLMException
from ..config.settings import Settings

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation"""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = 4096

    def _validate_config(self) -> None:
        """Validate OpenAI configuration"""
        if not self.settings.OPENAI_API_KEY:
            raise LLMException("OpenAI API key not configured")
        if not self.settings.OPENAI_MODEL:
            raise LLMException("OpenAI model not specified")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate(self, prompt: str) -> LLMResponse:
        """Generate response from OpenAI"""
        try:
            messages = [
                {"role": "system", "content": self._format_system_prompt()},
                {"role": "user", "content": prompt}
            ]

            response: ChatCompletion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=self.max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                raw_response=response.model_dump(),
                model=self.model,
                usage=response.usage.model_dump()
            )

        except Exception as e:
            raise LLMException(f"OpenAI API error: {str(e)}")

    async def validate_connection(self) -> bool:
        """Validate OpenAI connection"""
        try:
            await self.generate("test")
            return True
        except Exception as e:
            self.logger.error(f"OpenAI connection validation failed: {str(e)}")
            return False

    def _get_model_context_size(self) -> int:
        """Get model's context size"""
        context_sizes = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384
        }
        return context_sizes.get(self.model, 4096)
    
__all__ = ["OpenAIProvider"]

def create_llm_provider(settings: Settings) -> BaseLLMProvider:
    """Create and return an LLM provider instance"""
    if settings.LLM_PROVIDER == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        return OpenAIProvider(settings)
    
    raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")