import os
import pytest
from unittest.mock import patch, MagicMock
from src.llm import OpenAIProvider
import json

@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

def test_openai_chat_success():
    provider = OpenAIProvider()
    # Use raw JSON object instead of formatted string
    test_response = {
        "action": "create_issues",
        "issues": [
            {
                "project": "TEST",
                "summary": "Integration Test"
            }
        ]
    }
    
    fake_message = MagicMock()
    # Convert to consistent JSON string
    fake_message.content = json.dumps(test_response)
    fake_choice = MagicMock()
    fake_choice.message = fake_message
    fake_completion = MagicMock()
    fake_completion.choices = [fake_choice]

    with patch("openai.ChatCompletion.create", return_value=fake_completion) as mock_create:
        messages = [
            {"role": "user", "content": "Test command"}
        ]
        result = provider.chat(messages)
        
        # Verify system prompt and API call
        mock_create.assert_called_once_with(
            model=os.environ.get("OPENAI_MODEL"),
            messages=[
                {"role": "system", "content": """Return ONLY JSON with these exact fields:
        {
          "action": "create_issues",
          "issues": [
            {
              "project": "TEST",  // Must be uppercase
              "summary": "Task summary here"  // 5-255 characters
            }
          ]
        }"""},
                {"role": "user", "content": "Test command"}
            ],
            temperature=0
        )
        
        # Extract JSON from response and normalize
        result_content = result['message']['content']
        json_start = result_content.find('{')
        json_end = result_content.rfind('}') + 1
        actual_json = json.loads(result_content[json_start:json_end])
        
        # Compare normalized JSON objects
        assert actual_json == test_response

def test_openai_no_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY must be set for OpenAI API"):
        OpenAIProvider()