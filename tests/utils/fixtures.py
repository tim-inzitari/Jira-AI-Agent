from typing import Dict, Any

def get_mock_jira_issue() -> Dict[str, Any]:
    """Generate mock Jira issue data"""
    return {
        "key": "TEST-123",
        "fields": {
            "project": {"key": "TEST", "name": "Test Project"},
            "summary": "Test Issue",
            "description": "Test Description",
            "issuetype": {"name": "Task"},
            "priority": {"name": "Medium"}
        }
    }

def get_mock_llm_response() -> Dict[str, Any]:
    """Generate mock LLM response"""
    return {
        "actions": [{
            "type": "create_issue",
            "project": "TEST",
            "summary": "Test Issue",
            "description": "Test Description"
        }],
        "raw_response": "Creating issue in TEST project"
    }

def get_mock_api_error() -> Dict[str, Any]:
    """Generate mock API error response"""
    return {
        "success": False,
        "error": "API Error",
        "status_code": 500
    }