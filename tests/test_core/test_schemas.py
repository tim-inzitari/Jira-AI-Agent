import pytest
from pydantic import ValidationError
from src.core.schemas import (
    JiraIssueSchema,
    JiraActionSchema,
    LLMResponseSchema,
    CommandRequest,
    IssueType,
    IssuePriority
)

class TestSchemas:
    def test_issue_schema_validation(self):
        """Test issue schema validation"""
        # Valid case
        issue = JiraIssueSchema(
            project="TEST",
            summary="Test Issue",
            description="Test Description"
        )
        assert issue.project == "TEST"
        
        # Invalid case
        with pytest.raises(ValidationError):
            JiraIssueSchema(project="123", summary="")

    def test_action_schema_validation(self):
        """Test action schema validation"""
        # Valid case
        action = JiraActionSchema(
            type="create_issue",
            project="TEST",
            summary="Test Issue"
        )
        assert action.type == "create_issue"
        
        # Invalid case
        with pytest.raises(ValidationError):
            JiraActionSchema(type="invalid_type")

    def test_llm_response_schema(self):
        """Test LLM response schema"""
        response = LLMResponseSchema(
            actions=[{
                "type": "create_issue",
                "project": "TEST",
                "summary": "Test"
            }]
        )
        assert len(response.actions) == 1

    def test_enum_values(self):
        """Test enum values"""
        assert IssueType.TASK == "Task"
        assert IssuePriority.HIGH == "High"