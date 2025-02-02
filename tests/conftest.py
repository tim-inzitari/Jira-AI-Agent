import pytest
from typing import Dict, Any
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
import os
from src.config.settings import Settings
from src.core.agent import JiraAgent
from src.llm.base import BaseLLMProvider
from src.web.app import app
from src.web.dependencies import get_agent

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
def mock_agent() -> JiraAgent:
    """Provide mock agent instance"""
    agent = AsyncMock(spec=JiraAgent)
    agent.check_jira_connection = AsyncMock(return_value=True)
    agent.check_llm_connection = AsyncMock(return_value=True)
    # Fix: Return properly structured project data
    agent.get_projects = AsyncMock(return_value=[
        {
            "key": "TEST",
            "name": "Test Project",
            "description": "Test Description" 
        }
    ])
    return agent

@pytest.fixture
def test_client(mock_agent) -> TestClient:
    """Provide test client with mocked dependencies"""
    app.dependency_overrides[get_agent] = lambda: mock_agent
    yield TestClient(app)
    app.dependency_overrides.clear()  # Cleanup after test

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