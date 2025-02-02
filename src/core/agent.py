import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from jira import JIRA
import asyncio

from ..config.settings import Settings
from .schemas import (
    validate_action,
    validate_llm_response,  # Added import for validation
    JiraIssueSchema,
    ActionType,
    JiraError,
    JiraErrorType  # Ensure JiraErrorType is imported
)
from ..llm.base import BaseLLMProvider
from ..llm.factory import create_llm_provider

@dataclass
class JiraIssue:
    """Data structure for Jira issue details"""
    project: str
    summary: str
    description: Optional[str] = ""

class JiraAgent:
    """Jira agent for handling Jira operations"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Initialize Jira client
        self.jira = JIRA(
            server=str(settings.JIRA_SERVER),
            basic_auth=(settings.JIRA_USER, settings.JIRA_TOKEN)
        )
        
        # Initialize LLM provider
        self.llm = create_llm_provider(settings)
        
        # Protected projects
        self.protected_projects = settings.PROTECTED_PROJECTS.split(',')

    async def get_projects(self) -> List[Dict]:
        """Get list of available Jira projects"""
        try:
            # Run the synchronous Jira call in a thread pool
            loop = asyncio.get_running_loop()
            projects = await loop.run_in_executor(None, self.jira.projects)
            
            # Convert Jira project objects to dictionaries
            return [
                {
                    "key": project.key,
                    "name": project.name,
                    "description": getattr(project, "description", "")
                }
                for project in projects
            ]
        except Exception as e:
            self.logger.error(f"Failed to fetch projects: {str(e)}")
            raise JiraError(f"Failed to fetch projects: {str(e)}", JiraErrorType.UNKNOWN)

    async def process_command(self, command: str, project: str = None, dry_run: bool = False) -> List[Dict]:
        """Process natural language command"""
        if self._is_dangerous_command(command):
            raise JiraError("Command blocked: Contains restricted keywords", JiraErrorType.PERMISSION)  # Supply required error_type

        try:
            response = await self._get_llm_response(command)
            actions = self._parse_actions(response)
            if dry_run:
                # Implement dry run logic if necessary
                pass
            return await self._execute_actions(actions)
        except Exception as e:
            self.logger.error(f"Error processing command: {str(e)}", exc_info=True)
            raise

    def _is_dangerous_command(self, command: str) -> bool:
        """Improved dangerous command check"""
        DANGEROUS_KEYWORDS = {'delete', 'remove', 'drop', 'admin', 'password', 'token', 'key'}
        words = set(command.lower().split())
        return not DANGEROUS_KEYWORDS.isdisjoint(words)

    async def _get_llm_response(self, command: str) -> Dict:
        """Get validated response from LLM provider"""
        response = await self.llm.generate(command)
        
        # Convert Pydantic model to dict
        if hasattr(response, "dict"):
            response_data = response.dict()
        else:
            response_data = response  # Fallback if already a dict
        
        # Validate the response structure
        validate_llm_response(response_data)
    
        return response_data
    
    def _parse_actions(self, response: Dict) -> List[Dict]:
        """Parse and validate LLM response into actions"""
        actions = []
        for action in response.get('actions', []):
            validate_action(action)  # Ensure this checks for 'project' field
            
            # Add explicit project check
            if 'project' not in action:
                raise JiraError("Missing project in action", JiraErrorType.VALIDATION)
                
            if action['project'] in self.protected_projects:
                raise JiraError(
                    f"Access denied to protected project: {action['project']}",
                    JiraErrorType.PERMISSION
                )
            actions.append(action)
        return actions
    
    async def _execute_actions(self, actions: List[Dict]) -> List[Dict]:
        """Execute validated actions"""
        results = []
        for action in actions:
            # Execute action logic here
            results.append(action)
        return results

    async def _execute_single_action(self, action: Dict) -> Dict:
        """Execute a single validated action"""
        try:
            # Execute logic for a single action
            return action
        except Exception as e:
            self.logger.error(f"Error executing action: {str(e)}", exc_info=True)
            raise

    async def validate_connection(self) -> bool:
        """Validate Jira connection by invoking projects method"""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.jira.projects)
        return True

    async def check_jira_connection(self) -> bool:
        """Check Jira connection status"""
        try:
            # Create a future for the synchronous projects() call
            loop = asyncio.get_running_loop()
            # Run the synchronous Jira call in a thread pool
            await loop.run_in_executor(None, self.jira.projects)
            return True
        except Exception as e:
            self.logger.error(f"Jira connection check failed: {str(e)}")
            return False

    async def check_llm_connection(self) -> bool:
        """Check LLM connection status"""
        try:
            await self.llm.generate("test")
            return True
        except Exception as e:
            self.logger.error(f"LLM connection check failed: {str(e)}")
            return False