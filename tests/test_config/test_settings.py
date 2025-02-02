import pytest
from pydantic import ValidationError
from src.config.settings import Settings
import os
def test_settings_validation():
    """Test settings validation"""
    with pytest.raises(ValidationError):
        Settings(
            OLLAMA_HOSTNAME="",
            OLLAMA_PORT=-1,
            OLLAMA_HOST="invalid-url",
            JIRA_SERVER="invalid-url",
            JIRA_USER="invalid-email",
            JIRA_TOKEN="",
        )

def test_settings_defaults():
    """Test default settings values"""
    settings = Settings(
        OLLAMA_HOSTNAME="test-host",
        OLLAMA_HOST="http://test-host:11434",
        JIRA_SERVER="https://test.atlassian.net",
        JIRA_USER="test@example.com",
        JIRA_TOKEN="test-token"
    )
    assert settings.OLLAMA_PORT == 11434
    assert settings.DRY_RUN is False
    assert settings.LLM_PROVIDER == "ollama"

def test_settings_environment_override(monkeypatch):
    """Test environment variable override"""
    monkeypatch.setenv("OLLAMA_PORT", "8080")
    monkeypatch.setenv("DRY_RUN", "true")
    
    settings = Settings(
        OLLAMA_HOSTNAME="test-host",
        OLLAMA_HOST="http://test-host:8080",
        JIRA_SERVER="https://tsinzitari.atlassian.net",
        JIRA_USER="tsinzitari@gmail.com.com",
        JIRA_TOKEN=os.environ.get("JIRA_TOKEN")
    )
    
    assert settings.OLLAMA_PORT == 8080
    assert settings.DRY_RUN is True