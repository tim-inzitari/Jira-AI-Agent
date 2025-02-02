import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.agent import JiraAgent
from src.core.schemas import JiraError, JiraErrorType
from src.llm.base import LLMResponse
from tests.utils.mocks import MockJiraAPI, MockLLMAPI  # Import your mock APIs

@pytest.mark.asyncio
class TestJiraAgent:
    
    @pytest.fixture
    def settings(self):
        """Provide test settings"""
        from src.config.settings import Settings
        return Settings(
            PROTECTED_PROJECTS="PROD,LIVE",
            JIRA_SERVER="https://test.atlassian.net",
            JIRA_USER="test@example.com", 
            JIRA_TOKEN="test-token",
            LLM_PROVIDER="ollama",  # Must be ollama or openai
            OLLAMA_HOST="http://test:11434",
            OPENAI_API_KEY="test-key",
            DRY_RUN=True
        )

    @pytest.fixture
    def mock_jira(self):
        mock = MagicMock()
        mock.projects = AsyncMock(return_value=[])
        mock.myself = AsyncMock(return_value={"name": "test"})
        return mock

    @pytest.fixture
    def mock_llm(self):
        mock = AsyncMock()
        mock.generate = AsyncMock()
        return mock

    @pytest.fixture
    def agent(self, settings, mock_llm, mock_jira):
        with patch('src.core.agent.JIRA') as jira_mock, \
             patch('src.core.agent.create_llm_provider') as llm_mock:
            jira_mock.return_value = mock_jira
            llm_mock.return_value = mock_llm
            agent_obj = JiraAgent(settings)
            return agent_obj

    async def test_agent_initialization(self, settings, mock_jira, mock_llm):
        with patch('src.core.agent.JIRA', return_value=mock_jira), \
             patch('src.core.agent.create_llm_provider', return_value=mock_llm):
            
            agent = JiraAgent(settings)
            assert agent.jira is not None 
            assert agent.llm is not None

            # Verify initialization called the mocks
            mock_jira.myself.assert_called_once()
            assert agent.settings == settings

    async def test_process_command_success(self, agent):
        # Create valid LLMResponse with required fields
        agent.llm.generate.return_value = LLMResponse(
            content="Test response content",
            actions=[{"type": "create_issue", "project": "TEST", "summary": "Test issue"}],
            model="test-model"
        )
        
        result = await agent.process_command("test command")
        assert len(result) == 1
        assert result[0]["type"] == "create_issue"
        agent.llm.generate.assert_called_once()

    async def test_dangerous_command_blocked(self, agent):
        # Valid response format with empty actions
        agent.llm.generate.return_value = LLMResponse(
            content="Blocked command response",
            actions=[],  # Empty actions list
            model="test-model"
        )
        
        with pytest.raises(JiraError) as exc:
            await agent.process_command("delete all issues")
        assert exc.value.error_type == JiraErrorType.PERMISSION

    async def test_protected_project_access(self, agent):
        # Mock response with proper actions structure
        agent.llm.generate.return_value = LLMResponse(
            content="Test content",
            actions=[{"type": "create_issue", "project": "PROD", "summary": "Test"}],
            model="test"
        )
        
        with pytest.raises(JiraError) as exc:
            await agent.process_command("Create issue in PROD")
        
        assert exc.value.error_type == JiraErrorType.PERMISSION
        assert "PROD" in str(exc.value)

    async def test_connection_validation(self, agent):
        result = await agent.validate_connection()
        assert result is True
        agent.jira.projects.assert_called_once()

    async def test_error_handling(self, agent):
        agent.llm.generate.side_effect = Exception("LLM Error")
        with pytest.raises(Exception) as exc:
            await agent.process_command("test")
        assert "LLM Error" in str(exc.value)
