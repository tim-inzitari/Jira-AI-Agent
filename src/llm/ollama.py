import aiohttp
import json
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseLLMProvider, LLMResponse, LLMException
from ..config.settings import Settings

class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider implementation"""
    
    def __init__(self, settings: Settings):
        # Set attributes before super().__init__
        self.model = settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_HOST
        self.timeout = aiohttp.ClientTimeout(total=300)
        
        # Now call super() which will call _validate_config
        super().__init__(settings)
        
    def _validate_config(self) -> None:
        """Validate Ollama configuration"""
        if not self.settings.OLLAMA_IP:
            raise LLMException("Ollama IP address not configured")
        if not self.model or ':' not in self.model:
            raise LLMException("Invalid Ollama model format. Expected format: name:tag")

    async def _check_model_availability(self) -> bool:
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status != 200:
                        return False
                    tags = await response.json()
                    return any(self.model in tag["name"] for tag in tags["models"])
        except:
            return False

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
                    result = await response.json()
                    if "response" not in result:
                        raise LLMException(f"Ollama API error: missing 'response' in JSON: {result}")
                    return LLMResponse(
                        content=result["response"],
                        raw_response=result,
                        model=self.model
                    )
        except Exception as e:
            raise LLMException(f"Ollama API error: {str(e)}")

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