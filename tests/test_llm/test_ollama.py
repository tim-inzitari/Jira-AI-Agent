import pytest
import aiohttp
from unittest.mock import patch, AsyncMock
from src.llm.ollama import OllamaProvider
from src.llm.base import LLMException

@pytest.mark.asyncio
class TestOllamaProvider:
    async def test_generate_success(self, settings):
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "response": "test response"
            }
            mock_post.return_value.__aenter__.return_value = mock_response
            
            provider = OllamaProvider(settings)
            response = await provider.generate("test prompt")
            assert response.content == "test response"

    async def test_generate_error(self, settings):
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.side_effect = aiohttp.ClientError
            
            provider = OllamaProvider(settings)
            with pytest.raises(LLMException):
                await provider.generate("test prompt")

    async def test_validate_connection(self, settings):
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value.status = 200
            
            provider = OllamaProvider(settings)
            assert await provider.validate_connection()