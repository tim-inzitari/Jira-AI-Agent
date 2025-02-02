from typing import Dict, Any, List
from unittest.mock import AsyncMock, Mock

class MockJiraAPI:
    """Mock Jira API responses"""
    
    @staticmethod
    def create_issue() -> AsyncMock:
        """Mock Jira create_issue response"""
        mock = AsyncMock()
        mock.return_value = Mock(
            key="TEST-123",
            permalink=lambda: "https://tsinzitari.atlassian.net/browse/TEST-123"
        )
        return mock

    @staticmethod
    def get_projects() -> AsyncMock:
        """Mock Jira get_projects response"""
        mock = AsyncMock()
        mock.return_value = [
            Mock(key="TEST", name="Test Project"),
            Mock(key="DEV", name="Development Project")
        ]
        return mock

    @staticmethod
    def transition_issue() -> AsyncMock:
        """Mock Jira transition_issue response"""
        mock = AsyncMock()
        mock.return_value = Mock(success=True)
        return mock

class MockLLMAPI:
    """Mock LLM API responses"""
    
    @staticmethod
    def generate() -> AsyncMock:
        """Mock LLM API successful response"""
        mock = AsyncMock()
        mock.return_value = {
            "content": "Creating issue in TEST project",
            "actions": [{
                "type": "create_issue",
                "project": "TEST",
                "summary": "Test Issue"
            }]
        }
        return mock

    @staticmethod
    def error_response() -> AsyncMock:
        """Mock LLM API error response"""
        mock = AsyncMock()
        mock.side_effect = Exception("LLM API Error")
        return mock
