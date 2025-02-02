from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging
from ..config.settings import Settings

class LLMResponse(BaseModel):
    """Standardized LLM response format"""
    content: str
    actions: List[Dict] = Field(default_factory=list)
    raw_response: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    
class LLMException(Exception):
    """Base exception for LLM-related errors"""
    pass

class BaseLLMProvider(ABC):
    """Base class for LLM providers"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self._validate_config()

    @abstractmethod
    async def generate(self, prompt: str) -> LLMResponse:
        """Generate response from LLM"""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate connection to LLM service"""
        pass

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider configuration"""
        pass

    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize input prompt"""
        return prompt.strip()

    def _format_system_prompt(self) -> str:
        """Format system prompt for context"""
        return """You are a Jira assistant. Your task is to:
1. Parse natural language commands
2. Convert them to Jira actions
3. Return structured responses
Format your responses as JSON with an 'actions' array."""

    async def process_prompt(self, prompt: str) -> LLMResponse:
        """Process prompt with error handling"""
        try:
            sanitized_prompt = self._sanitize_prompt(prompt)
            system_prompt = self._format_system_prompt()
            response = await self.generate(
                f"{system_prompt}\n\nUser request: {sanitized_prompt}"
            )
            return response
        except Exception as e:
            self.logger.error(f"LLM processing error: {str(e)}", exc_info=True)
            raise LLMException(f"Failed to process prompt: {str(e)}")

__all__ = ['LLMResponse', 'LLMException', 'BaseLLMProvider']