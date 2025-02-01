import os
import pytest
from unittest.mock import patch, MagicMock
from src.llm import OpenAIProvider

@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

def test_openai_chat_success():
    provider = OpenAIProvider()
    fake_response = MagicMock()
    fake_message = MagicMock()
    fake_message.content = "Test response from OpenAI"
    fake_choice = MagicMock()
    fake_choice.message = fake_message
    fake_completion = MagicMock()
    fake_completion.choices = [fake_choice]

    with patch("src.llm.openai.ChatCompletion.create", return_value=fake_completion) as mock_create:
        messages = [
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "Test command"}
        ]
        result = provider.chat(messages)
        mock_create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0
        )
        
        # Verify that the response is wrapped in <answer> tags
        expected_content = "<answer>Test response from OpenAI</answer>"
        assert result == {'message': {'content': expected_content}}

def test_openai_no_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY must be set for OpenAI API"):
        OpenAIProvider()