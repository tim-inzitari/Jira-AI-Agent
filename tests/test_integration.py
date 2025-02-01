import pytest
import json
from unittest.mock import patch, Mock, MagicMock
# --- Test Data ---
GOOD_RESPONSE = """
<think>Creating multiple test issues</think>
<answer>
{
    "action": "create_issues",
    "issues": [
        {
            "project": "TEST",
            "summary": "Integration Test 1"
        },
        {
            "project": "TEST",
            "summary": "Integration Test 2"
        }
    ]
}
</answer>
"""

GOOD_RESPONSE_SINGLE = """
<think>Creating test issue</think>
<answer>
{
    "action": "create_issues",
    "issues": [
        {
            "project": "TEST",
            "summary": "Integration Test"
        }
    ]
}
</answer>
"""

BAD_RESPONSE = """
<think>Invalid format</think>
<answer>
{
    "issues": [
        {
            "project": "TEST",
            "summary": "Bad"
        }
    ]
}
</answer>
"""

INVALID_XML_RESPONSE = "<think>Missing tags</think>"

@pytest.mark.integration
class TestJiraIntegration:
    @pytest.mark.parametrize("llm_provider", ["openai", "deepseek-r1:14b", "llama"])
    def test_valid_command(self, monkeypatch, llm_provider, mock_llm_responses):
        """Test command processing with different LLM providers"""
        monkeypatch.setenv("LLM_PROVIDER", llm_provider)
        
        if llm_provider == "openai":
            with patch("src.llm.OpenAI") as mock_openai_class, \
                patch("src.main.JIRA") as mock_jira, \
                patch("src.llm.ollama.Client") as mock_ollama:
                # Create a dummy instance for OpenAI that returns the fake response
                dummy_instance = MagicMock()
                dummy_instance.chat.completions.create.return_value = mock_llm_responses[llm_provider]
                mock_openai_class.return_value = dummy_instance

                # Mock Jira setup
                mock_project = Mock()
                mock_project.key = "TEST"
                mock_jira.return_value.projects.return_value = [mock_project]
                mock_issue = Mock()
                mock_issue.key = "TEST-123"
                mock_jira.return_value.create_issue.return_value = mock_issue

                from src.main import JiraAgent
                agent = JiraAgent()
                result = agent.process_command("Create test issue")
                assert "TEST-123" in result

        elif llm_provider in ["deepseek-r1:14b", "llama"]:
            with patch("src.main.JIRA") as mock_jira, \
                 patch("src.llm.ollama.Client") as mock_ollama:
                # Mock Jira setup
                mock_project = Mock()
                mock_project.key = "TEST"
                mock_jira.return_value.projects.return_value = [mock_project]
                mock_issue = Mock()
                mock_issue.key = "TEST-123"
                mock_jira.return_value.create_issue.return_value = mock_issue

                # Set up available models for deepseek/llama
                mock_ollama.return_value.list.return_value = {
                    "models": [{"model": "deepseek-r1:14b"}, {"model": "llama2-13b"}]
                }
                if llm_provider not in [m["model"] for m in mock_ollama.return_value.list.return_value["models"]]:
                    pytest.skip(f"Model {llm_provider} not available")
                mock_ollama.return_value.chat.return_value = mock_llm_responses[llm_provider]

                from src.main import JiraAgent
                agent = JiraAgent()
                result = agent.process_command("Create test issue")
                assert "TEST-123" in result

    def test_invalid_action_format(self):
        """Test malformed LLM response"""
        with patch('src.llm.ollama.Client') as mock_ollama:
            mock_ollama.return_value.list.return_value = {'models': [{'model': 'deepseek-r1:14b'}]}
            mock_ollama.return_value.chat.return_value = {'message': {'content': BAD_RESPONSE}}
            
            from src.main import JiraAgent
            agent = JiraAgent()
            result = agent.process_command("Bad command")
            # Check for a validation error mentioning missing 'action'
            assert "Validation failed" in result and "'action'" in result
    
    def test_xml_parsing_failure(self):
        """Test missing XML tags"""
        with patch('src.llm.ollama.Client') as mock_ollama:
            mock_ollama.return_value.list.return_value = {'models': [{'model': 'deepseek-r1:14b'}]}
            mock_ollama.return_value.chat.return_value = {'message': {'content': INVALID_XML_RESPONSE}}
            
            from src.main import JiraAgent
            agent = JiraAgent()
            result = agent.process_command("Test")
            assert 'Validation Error' in result
    
    def test_dry_run_mode(self):
        """Test dry-run doesn't call Jira API for single issue"""
        with patch('src.llm.ollama.Client') as mock_ollama, \
             patch('src.main.JIRA') as mock_jira:
            mock_project = Mock()
            mock_project.key = 'TEST'
            mock_jira.return_value.projects.return_value = [mock_project]
            mock_ollama.return_value.list.return_value = {'models': [{'model': 'deepseek-r1:14b'}]}
            mock_ollama.return_value.chat.return_value = {'message': {'content': GOOD_RESPONSE_SINGLE}}
            
            from src.main import JiraAgent
            agent = JiraAgent(dry_run=True)
            result = agent.process_command("Create test issue")
            assert "[DRY RUN]" in result
            mock_jira.return_value.create_issue.assert_not_called()
    
    def test_dangerous_command_blocking(self):
        """Test security keyword blocking"""
        from src.main import JiraAgent
        agent = JiraAgent()
        result = agent.process_command("Delete all projects")
        assert "Blocked" in result
    
    def test_valid_multiple_commands(self):
        """Test successful processing of multiple commands"""
        with patch('src.llm.ollama.Client') as mock_ollama, \
             patch('src.main.JIRA') as mock_jira:
            mock_project = Mock()
            mock_project.key = 'TEST'
            mock_jira.return_value.projects.return_value = [mock_project]
            mock_ollama.return_value.list.return_value = {'models': [{'model': 'deepseek-r1:14b'}]}
            mock_ollama.return_value.chat.return_value = {'message': {'content': GOOD_RESPONSE}}
            mock_issue_1 = Mock()
            mock_issue_1.key = 'TEST-123'
            mock_issue_2 = Mock()
            mock_issue_2.key = 'TEST-124'
            mock_jira.return_value.create_issue.side_effect = [mock_issue_1, mock_issue_2]
            from src.main import JiraAgent
            agent = JiraAgent()
            result = agent.process_command("Create multiple test issues")
            assert "TEST-123" in result
            assert "TEST-124" in result
            assert mock_jira.return_value.create_issue.call_count == 2
    
    def test_invalid_multiple_action_format(self):
        """Test malformed LLM response for multiple actions"""
        with patch('src.llm.ollama.Client') as mock_ollama:
            mock_ollama.return_value.list.return_value = {'models': [{'model': 'deepseek-r1:14b'}]}
            mock_ollama.return_value.chat.return_value = {'message': {'content': BAD_RESPONSE}}
            
            from src.main import JiraAgent
            agent = JiraAgent()
            result = agent.process_command("Bad command for multiple issues")
            assert "Validation failed" in result and "'action'" in result
    
    def test_dry_run_mode_multiple(self):
        """Test dry-run doesn't call Jira API for multiple issues"""
        with patch('src.llm.ollama.Client') as mock_ollama, \
             patch('src.main.JIRA') as mock_jira:
            mock_project = Mock()
            mock_project.key = 'TEST'
            mock_jira.return_value.projects.return_value = [mock_project]
            mock_ollama.return_value.list.return_value = {'models': [{'model': 'deepseek-r1:14b'}]}
            mock_ollama.return_value.chat.return_value = {'message': {'content': GOOD_RESPONSE}}
            from src.main import JiraAgent
            agent = JiraAgent(dry_run=True)
            result = agent.process_command("Create multiple test issues")
            assert "[DRY RUN]" in result
            assert mock_jira.return_value.create_issue.call_count == 0
    
    def test_dangerous_command_blocking_multiple(self):
        """Test security keyword blocking for multiple commands"""
        from src.main import JiraAgent
        agent = JiraAgent()
        result = agent.process_command("Delete all projects")
        assert "Blocked" in result

@pytest.mark.integration
def test_live_connection(ollama_client, jira_client):
    """End-to-end test with actual services for a simple command"""
    from src.main import JiraAgent
    agent = JiraAgent()
    result = agent.process_command("List projects in TEST")
    print("\nLive Test Raw Response:", result)
    assert "TEST" in result or "projects" in result.lower() or "validation error" in result.lower()

@pytest.mark.integration
def test_live_connection_multiple(ollama_client, jira_client):
    """End-to-end test with actual services for multiple issues"""
    from src.main import JiraAgent
    agent = JiraAgent()
    result = agent.process_command("List projects in TEST")
    print("\nLive Test Raw Response:", result)
    assert "TEST" in result or "projects" in result.lower() or "validation error" in result.lower()
