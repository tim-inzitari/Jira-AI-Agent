import openai
from typing import Any, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
import logging
from .base import BaseLLMProvider, LLMResponse, LLMException
from ..config.settings import Settings

def _retry_handler(retry_state):
    """Convert RetryError to LLMException"""
    exc = retry_state.outcome.exception()
    if isinstance(exc, LLMException):
        return exc
    raise LLMException(f"OpenAI API error after retries: {str(exc)}")

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation"""

    def __init__(self, settings: Settings):
        # Assign required attributes before BaseLLMProvider.__init__
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_tokens = 4096
        openai.api_key = self.api_key

        # Set settings and logger explicitly so the base __init__ doesn't overwrite.
        self.settings = settings
        self.logger = logging.getLogger(__name__)

        # Now call the base initializer which will call _validate_config (our override)
        super().__init__(settings)

    def _validate_config(self) -> None:
        """Validate OpenAI configuration"""
        if not self.api_key:
            raise LLMException("OpenAI API key not configured")
        if not self.model:
            raise LLMException("OpenAI model not specified")

    def _get_model_context_size(self) -> int:
        """Return model context size"""
        context_sizes = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384
        }
        return context_sizes.get(self.model, 4096)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=100),
        reraise=True  # Let exceptions propagate
    )
    async def generate(self, prompt: str) -> LLMResponse:
        """Generate response from OpenAI"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
            )
            if not response or not response.choices:
                raise LLMException("Failed to get valid response from OpenAI")
            
            choice = response.choices[0]
            raw_resp = vars(response) if not isinstance(response, dict) else response
            
            llm_response = LLMResponse(
                content=choice.message.content,
                raw_response=raw_resp,
                model=self.model,
                usage=response.usage
            )
            return llm_response
        except Exception as e:
            if isinstance(e, LLMException):
                raise
            raise LLMException(f"OpenAI API error: {str(e)}")
            
    async def validate_connection(self) -> bool:
        """Validate OpenAI connection"""
        try:
            await self.generate("test")
            return True
        except Exception as e:
            self.logger.error(f"OpenAI connection validation failed: {str(e)}")
            return False

__all__ = ["OpenAIProvider"]

def create_llm_provider(settings: Settings) -> BaseLLMProvider:
    """Create and return an LLM provider instance"""
    if settings.LLM_PROVIDER == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        return OpenAIProvider(settings)
    
    raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")