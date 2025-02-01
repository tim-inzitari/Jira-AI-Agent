import os
import pytest
from unittest.mock import Mock, MagicMock
import ollama
from jira import JIRA
from dotenv import load_dotenv

load_dotenv()  # Load from project root

# --- Safety Configuration ---
TEST_PROJECT = "TEST"  # Your test project key
BLACKLISTED_PROJECTS = ["PROD", "LIVE"]  # Production projects to protect

# --- Test Data ---
@pytest.fixture
def mock_llm_responses():
    """Standard test responses for different LLM providers"""
    openai_mock = MagicMock()
    openai_mock.choices = [
        MagicMock(
            message=MagicMock(
                content="""{"action": "create_issues", "issues": [{"project": "TEST", "summary": "Integration Test"}]}"""
            )
        )
    ]
    return {
        "openai": openai_mock,
        "deepseek-r1:14b": {
            "message": {
                "content": """<answer>{"action": "create_issues", "issues": [{"project": "TEST", "summary": "Integration Test"}]}</answer>"""
            }
        }
    }

# --- LLM Provider Configuration ---
@pytest.fixture(params=["openai", "deepseek-r1:14b", "llama"])
def llm_provider(request, monkeypatch):
    """Parametrized fixture for different LLM providers"""
    provider = request.param
    monkeypatch.setenv("LLM_PROVIDER", provider)
    
    if provider == "openai":
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-3.5-turbo")
    elif provider == "llama":
        pytest.skip("Llama model not available")
    
    return provider

# --- Service Client Fixtures ---
@pytest.fixture(scope="session")
def ollama_client():
    """Validated Ollama connection"""
    try:
        client = ollama.Client(host=os.getenv("OLLAMA_HOST"))
        models = client.list()
        if "deepseek-r1:14b" not in [m["model"] for m in models["models"]]:
            pytest.skip("deepseek-r1:14b model not available")
        return client
    except Exception as e:
        pytest.skip(f"Ollama connection failed: {str(e)}")

@pytest.fixture(scope="session")
def jira_client():
    """Validated Jira connection"""
    try:
        client = JIRA(
            server=os.getenv("JIRA_SERVER"),
            basic_auth=(os.getenv("JIRA_USER"), os.getenv("JIRA_TOKEN"))
        )
        _ = client.projects()
        return client
    except Exception as e:
        pytest.skip(f"Jira connection failed: {str(e)}")

# --- Agent Fixture ---
@pytest.fixture
def agent(jira_client, ollama_client):
    """Pre-configured JiraAgent instance with dry-run"""
    from src.main import JiraAgent
    return JiraAgent(dry_run=True)  # Enable dry-run for tests

# --- Environment Setup ---
@pytest.fixture(autouse=True)
def set_openai_env(monkeypatch):
    """Ensure OpenAI environment variables are set for tests"""
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-api-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-3.5-turbo")
