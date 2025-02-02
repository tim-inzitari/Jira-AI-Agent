import pytest
from unittest.mock import patch, AsyncMock
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage as Message
from src.llm.openai import OpenAIProvider
from src.llm.base import LLMException
from typing import Dict  # ✅ Fix for missing Dict import


# Define mock classes to match OpenAI types
class MockMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class MockChoice:
    def __init__(self, index: int, message: MockMessage):
        self.index = index
        self.message = message

class MockChatCompletion:
    def __init__(self, id: str, choices: list, model: str, usage: Dict[str, int]):
        self.id = id
        self.choices = choices
        self.model = model
        self.usage = usage

@pytest.mark.asyncio
class TestOpenAIProvider:
    async def test_generate_success(self, settings):
        mock_response = ChatCompletion(
            id="test",
            choices=[
                Choice(
                    index=0,
                    message=Message(
                        role="assistant",
                        content="test response"
                    )
                )
            ],
            model="gpt-4",
            usage={"total_tokens": 10}
        )
        
        with patch("openai.AsyncOpenAI.chat.completions.create") as mock_create:
            mock_create.return_value = mock_response
            
            provider = OpenAIProvider(settings)
            response = await provider.generate("test prompt")
            assert response.content == "test response"

    async def test_generate_error(self, settings):
        with patch("openai.AsyncOpenAI.chat.completions.create") as mock_create:
            mock_create.side_effect = Exception("API Error")
            
            provider = OpenAIProvider(settings)
            with pytest.raises(LLMException):
                await provider.generate("test prompt")

    def test_get_model_context_size(self, settings):
        provider = OpenAIProvider(settings)
        assert provider._get_model_context_size() == 8192