import os
import pytest
import ollama
from jira import JIRA
from dotenv import load_dotenv

load_dotenv()  # Load from project root

# --- Safety Configuration ---
TEST_PROJECT = "TEST"  # Your test project key
BLACKLISTED_PROJECTS = ["PROD", "LIVE"]  # Production projects to protect

@pytest.fixture(scope="session")
def ollama_client():
    """Validated Ollama connection"""
    try:
        client = ollama.Client(host=os.getenv("OLLAMA_HOST"))
        models = client.list()
        
        # Corrected model key access
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
        # Verify connection
        _ = client.projects()
        return client
    except Exception as e:
        pytest.skip(f"Jira connection failed: {str(e)}")

@pytest.fixture
def agent(jira_client, ollama_client):
    """Pre-configured JiraAgent instance"""
    from src.main import JiraAgent
    return JiraAgent()

@pytest.fixture
def agent(jira_client, ollama_client):
    """Pre-configured JiraAgent instance with dry-run"""
    from src.main import JiraAgent
    return JiraAgent(dry_run=True)  # Enable dry-run for tests

@pytest.fixture(autouse=True)
def set_openai_env(monkeypatch):
    # Ensure that a dummy API key and model are set for tests that instantiate OpenAIProvider.
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-api-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-3.5-turbo")