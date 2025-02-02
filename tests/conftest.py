import pytest
from typing import Dict, Any
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
import os
from src.config.settings import Settings
from src.core.agent import JiraAgent
from src.llm.base import BaseLLMProvider
from src.web.app import app

@pytest.fixture
def settings() -> Settings:
    """Provide test settings"""
    return Settings(
        OLLAMA_HOSTNAME="test-ollama",
        OLLAMA_PORT=11434,
        OLLAMA_HOST="http://test-ollama:11434",
        JIRA_SERVER="https://tsinzitari.atlassian.net",
        JIRA_USER="tsinzitari@gmail.com",
        JIRA_TOKEN=os.environ.get("JIRA_TOKEN"),
        LLM_PROVIDER="ollama",
        OPENAI_API_KEY="test-key",
        DRY_RUN=True,
        PROTECTED_PROJECTS="PROD,LIVE"
    )

@pytest.fixture
def mock_jira_client() -> AsyncMock:
    """Provide mock Jira client"""
    client = AsyncMock()
    client.projects.return_value = [
        Mock(key="TEST", name="Test Project"),
        Mock(key="DEV", name="Development")
    ]
    client.create_issue.return_value = Mock(
        key="TEST-123",
        permalink=lambda: "https://test.atlassian.net/browse/TEST-123"
    )
    client.myself.return_value = {"name": "test_user"}
    return client

@pytest.fixture
def mock_llm_response() -> Dict[str, Any]:
    """Provide mock LLM response"""
    return {
        "actions": [{
            "type": "create_issue",
            "project": "TEST",
            "summary": "Test Issue",
            "description": "Test Description"
        }]
    }

@pytest.fixture
def mock_llm_provider(mock_llm_response) -> AsyncMock:
    """Provide mock LLM provider"""
    provider = AsyncMock(spec=BaseLLMProvider)
    provider.generate.return_value = mock_llm_response
    return provider

@pytest.fixture
def mock_agent(settings, mock_jira_client, mock_llm_provider) -> JiraAgent:
    """Provide mock agent instance"""
    with patch('src.core.agent.JIRA', return_value=mock_jira_client):
        agent = JiraAgent(settings)
        agent.jira = mock_jira_client
        agent.llm = mock_llm_provider
        return agent

@pytest.fixture
def test_client(mock_agent) -> TestClient:
    """Provide FastAPI test client"""
    app.dependency_overrides = {}
    return TestClient(app)

@pytest.fixture
def mock_http_response() -> Dict[str, Any]:
    """Provide mock HTTP response"""
    return {
        "status_code": 200,
        "content": "Test content",
        "headers": {"Content-Type": "application/json"}
    }

@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests"""
    import logging
    logging.basicConfig(level=logging.DEBUG)