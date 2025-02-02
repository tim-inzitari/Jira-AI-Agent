from typing import Optional

class JiraAIError(Exception):
    """Base exception for Jira AI Agent."""
    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)