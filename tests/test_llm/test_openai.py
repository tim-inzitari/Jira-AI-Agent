from types import SimpleNamespace
import pytest
from unittest.mock import patch, AsyncMock
from src.llm.openai import OpenAIProvider
from src.llm.base import LLMException

@pytest.mark.asyncio
class TestOpenAIProvider:
    async def test_generate_success(self, settings):
        simulated_response = SimpleNamespace(
            id="test",
            choices=[
                SimpleNamespace(
                    index=0,
                    message=SimpleNamespace(role="assistant", content="test response"),
                    finish_reason="stop"
                )
            ],
            model="gpt-4",
            usage={"total_tokens": 10}
        )
        # Patch the openai.ChatCompletion.acreate used in our module
        with patch("src.llm.openai.openai.ChatCompletion.acreate", new=AsyncMock(return_value=simulated_response)):
            provider = OpenAIProvider(settings)
            response = await provider.generate("test prompt")
            assert response.content == "test response"

    async def test_generate_error(self, settings):
        with patch("src.llm.openai.openai.ChatCompletion.acreate", new=AsyncMock(side_effect=Exception("API Error"))):
            provider = OpenAIProvider(settings)
            with pytest.raises(LLMException) as exc_info:
                await provider.generate("test prompt")
            assert "API Error" in str(exc_info.value)

    def test_get_model_context_size(self, settings):
        provider = OpenAIProvider(settings)
        assert provider.api_key == settings.OPENAI_API_KEY
        # Assuming settings for a default model "gpt-4"
        assert provider._get_model_context_size() == 8192