# Jira AI Agent 🤖📋

An AI-powered interface for Jira task management via natural language commands.

[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker)]
[![Jira](https://img.shields.io/badge/Jira-Integrated-0052CC?logo=jira)]
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)]

# Features
- Web interface (FastAPI + HTMX)
- CLI version for terminal use
- Natural language processing via Ollama
- Jira API integration
- Safety validation layers
- Dry-run testing mode

# Quick Start
1. Clone repo:
git clone https://github.com/YOUR_USER/jira-ai-agent.git
cd jira-ai-agent

2. Configure environment:
cp .env.example .env
nano .env  # Edit credentials

3. Start services:
docker-compose up --build web

# Web Interface
Access at: http://localhost:8000
- Type commands in textbox
- Real-time responses
- Error highlighting

# CLI Usage
docker-compose run --rm cli
Example: "Create task in TEST: Update docs"

## Configuration (.env)

Ensure that your .env file includes the new variables:

  • LLM_PROVIDER – Set to one of: deepseek, openai, or llama  
  • OPENAI_API_KEY – Provide your OpenAI API key when using the OpenAI provider

Example:

OLLAMA_HOST=http://YOUR_OLLAMA_IP:11434
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_USER=your@email.com
JIRA_TOKEN=your_api_token
DRY_RUN=false

# Troubleshooting
- Clean rebuild: docker-compose down --remove-orphans && docker-compose build --no-cache
- Test connections: curl $OLLAMA_HOST/api/tags
- Check logs: docker-compose logs web

# Roadmap
- [x] Web interface
- [x] Multi-step commands
- [ ] User authentication
- [ ] Slack integration

# License
MIT License - Use at your own risk

# Testing

To run tests, use the following command:

```bash
pytest
```

Here is an example test file:

```python
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