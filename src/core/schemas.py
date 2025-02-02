from enum import Enum
from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field, validator, field_validator, ConfigDict

class JiraErrorType(Enum):
    """Jira error types"""
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    NOT_FOUND = "not_found"
    VALIDATION = "validation"
    UNKNOWN = "unknown"

class JiraError(Exception):
    """Custom Jira exception"""
    def __init__(self, message: str, error_type: JiraErrorType):
        self.error_type = error_type
        super().__init__(message)

class IssueType(str, Enum):
    TASK = "Task"
    BUG = "Bug"
    STORY = "Story"
    EPIC = "Epic"

class IssuePriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class ActionType(str, Enum):
    CREATE = "create_issue"
    UPDATE = "update_issue"
    COMMENT = "comment_issue"
    TRANSITION = "transition_issue"

class JiraIssueSchema(BaseModel):
    project: str
    summary: str
    description: Optional[str] = ""

    model_config = ConfigDict(extra='forbid')

    @field_validator('project')
    def validate_project(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Project key must be alphanumeric")
        return v.upper()

    @field_validator('summary')
    def validate_summary(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Summary cannot be empty")
        return v

class JiraActionSchema(BaseModel):
    type: Literal["create_issue", "update_issue", "transition_issue"]
    project: str  
    summary: str
    description: Optional[str] = ""

    model_config = ConfigDict(extra='allow')

class LLMResponseSchema(BaseModel):
    success: bool = True
    message: str = ""
    actions: List[Dict[str, Any]]

class CommandRequest(BaseModel):
    """Command request schema"""
    command: str
    project: Optional[str] = None
    dry_run: bool = False

    @field_validator('project')
    def validate_project(cls, v):
        if v and not v.isalnum():
            raise ValueError("Project key must be alphanumeric")
        return v

    class Config:
        json_schema_extra = {  # Changed from schema_extra
            "example": {
                "command": "Create a bug ticket for login page",
                "project": "PROJ",
                "dry_run": False
            }
        }

class CommandResponseSchema(BaseModel):
    success: bool
    message: str
    actions: Optional[List[Dict[str, Any]]] = None
    errors: Optional[List[str]] = None

def validate_action(action: Dict[str, Any]) -> None:
    """Validate action against schema"""
    try:
        JiraActionSchema(**action)
    except Exception as e:
        raise ValueError(f"Invalid action format: {str(e)}")

def validate_llm_response(response: Dict[str, Any]) -> None:
    """Validate LLM response structure"""
    if not isinstance(response.get('actions'), list):
        raise ValueError("LLM response must contain 'actions' list")
    try:
        LLMResponseSchema(**response)
    except Exception as e:
        raise ValueError(f"Invalid LLM response format: {str(e)}")