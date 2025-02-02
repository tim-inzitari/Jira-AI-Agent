import pytest
from src.llm.base import BaseLLMProvider, LLMResponse, LLMException

class MockLLMProvider(BaseLLMProvider):
    async def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(content="test response")
    
    async def validate_connection(self) -> bool:
        return True
        
    def _validate_config(self) -> None:
        pass

@pytest.mark.asyncio
class TestBaseLLMProvider:
    async def test_process_prompt(self, settings):
        provider = MockLLMProvider(settings)
        response = await provider.process_prompt("test")
        assert isinstance(response, LLMResponse)
        assert response.content == "test response"

    async def test_sanitize_prompt(self, settings):
        provider = MockLLMProvider(settings)
        assert provider._sanitize_prompt(" test ") == "test"

    def test_format_system_prompt(self, settings):
        provider = MockLLMProvider(settings)
        prompt = provider._format_system_prompt()
        assert "Jira assistant" in prompt