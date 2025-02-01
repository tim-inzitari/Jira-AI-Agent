import os
import pytest
from unittest.mock import patch, MagicMock
from src.llm import OpenAIProvider
import json

@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-3.5-turbo")

def test_openai_chat_success(mock_llm_responses):
    """Test OpenAI chat with a dummy instance created via patching the constructor"""
    # Patch the OpenAI class as imported in src.llm
    with patch("src.llm.OpenAI") as mock_openai_class:
        # Create a dummy instance with the desired attribute
        dummy_instance = MagicMock()
        dummy_instance.chat.completions.create.return_value = mock_llm_responses["openai"]
        mock_openai_class.return_value = dummy_instance

        # Now when we create an OpenAIProvider, it will use our dummy_instance
        provider = OpenAIProvider()
        messages = [
            {"role": "user", "content": "Test command"}
        ]
        result = provider.chat(messages)
        
        # Verify that our dummy method was called
        dummy_instance.chat.completions.create.assert_called_once()
        
        # Extract the JSON from the returned content
        result_content = result['message']['content']
        json_start = result_content.find('{')
        json_end = result_content.rfind('}') + 1
        actual_json = json.loads(result_content[json_start:json_end])
        expected_json = json.loads(mock_llm_responses["openai"].choices[0].message.content)
        
        assert actual_json == expected_json

def test_openai_no_api_key(monkeypatch):
    """Test OpenAI provider fails without API key"""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY must be set for OpenAI API"):
        OpenAIProvider()
