import aiohttp
import json
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseLLMProvider, LLMResponse, LLMException
from ..config.settings import Settings

class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider implementation"""
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.base_url = settings.OLLAMA_HOST  # Use the computed property
        self.model = settings.OLLAMA_MODEL
        self.timeout = aiohttp.ClientTimeout(total=30)

    def _validate_config(self) -> None:
        """Validate Ollama configuration"""
        if not self.settings.OLLAMA_IP:  # Check IP instead of HOST
            raise LLMException("Ollama IP address not configured")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=100),
        reraise=True
    )
    async def generate(self, prompt: str) -> LLMResponse:
        """Generate response from Ollama"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                ) as response:
                    if response.status != 200:
                        raise LLMException(f"Ollama API error: {response.status}")
                    
                    result = await response.json()
                    return LLMResponse(
                        content=result.get("response", ""),
                        raw_response=result,
                        model=self.model,
                        usage={
                            "prompt_tokens": len(prompt.split()),
                            "completion_tokens": len(
                                result.get("response", "").split()
                            )
                        }
                    )
        except aiohttp.ClientError as e:
            raise LLMException(f"Ollama connection error: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMException(f"Invalid JSON response: {str(e)}")

    async def validate_connection(self) -> bool:
        """Validate connection to Ollama server"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/version") as response:
                    return response.status == 200
        except Exception as e:
            self.logger.error(f"Ollama connection validation failed: {str(e)}")
            return False

__all__ = ["OllamaProvider"]