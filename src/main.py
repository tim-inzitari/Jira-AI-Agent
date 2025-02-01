import os
import json
import re
import logging
import ollama
from jira import JIRA
from dotenv import load_dotenv
from src.schemas import validate_action

load_dotenv()

DEEPSEEK_SYSTEM_PROMPT = """Return ONLY JSON with these exact fields:
{
  "action": "create_issues",
  "issues": [
    {
      "project": "TEST",  // Must be uppercase
      "summary": "Task summary here"  // 5-255 characters
    }
  ]
}"""

class JiraAgent:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self._init_jira()
        self._init_llm()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def _init_jira(self):
        """Initialize JIRA connection with validation"""
        try:
            self.jira = JIRA(
                server=os.getenv('JIRA_SERVER'),
                basic_auth=(
                    os.getenv('JIRA_USER'),
                    os.getenv('JIRA_TOKEN')
                )
            )
            _ = self.jira.projects()
        except Exception as e:
            raise ConnectionError(f"JIRA connection failed: {str(e)}")
        
    def _init_llm(self):
        """Initialize Ollama client with model check"""
        self.llm = ollama.Client(host=os.getenv('OLLAMA_HOST'))
        try:
            models = self.llm.list()
            if not any(m["model"].lower() == "deepseek-r1:14b" for m in models["models"]):
                raise ValueError("deepseek-r1:14b model not available")
        except Exception as e:
            raise ConnectionError(f"Ollama connection failed: {str(e)}")

    def process_command(self, command: str) -> str:
        """Process user command with validation pipeline"""
        if self._is_dangerous_command(command):
            return "Blocked: Command contains restricted keywords"
            
        try:
            response = self.llm.chat(
                model='deepseek-r1:14b',
                messages=[
                    {"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT},
                    {"role": "user", "content": command}
                ]
            )
            
            response_data = self._parse_response(response)
            actions = self._extract_actions(response_data)
            return self._execute_actions(actions)
            
        except json.JSONDecodeError as jde:
            return f"Error: Invalid JSON format - {str(jde)}"
        except ValueError as ve:
            return f"Validation Error: {str(ve)}"
        except KeyError as ke:
            return f"Configuration Error: {str(ke)}"
        except Exception as e:
            self.logger.error(f"System Error: {str(e)}", exc_info=True)
            return f"System Error: {str(e)}"

    def _is_dangerous_command(self, command: str) -> bool:
        """Check for potentially dangerous operations"""
        BLACKLISTED_KEYWORDS = ['delete', 'drop', 'admin', 'password', 'token']
        return any(kw in command.lower() for kw in BLACKLISTED_KEYWORDS)

    def _parse_response(self, response: dict) -> dict:
        """Parse and validate response structure"""
        try:
            content = response['message']['content']
            
            # Extract content between <answer> tags
            answer_match = re.search(r'<answer>(.*?)</answer>', content, re.DOTALL)
            if answer_match:
                json_str = answer_match.group(1)
            else:
                # Fallback: extract JSON block from entire content
                json_match = re.search(r'({.*})', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    raise ValueError("No valid JSON found in response")
                
            return json.loads(json_str)
            
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON structure in LLM response")

    def _extract_actions(self, response_data: dict) -> list:
        """Extract and validate actions"""
        try:
            issues = response_data["issues"]
            # If top-level "action" indicates multiple issues, add the proper action to each issue.
            if "action" in response_data and response_data["action"] == "create_issues":
                for issue in issues:
                    issue["action"] = "create_issue"
            for action in issues:
                action["project"] = action["project"].upper()
                validate_action(action)
            return issues
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e)}")

    def _execute_actions(self, actions: list) -> str:
        """Execute validated JIRA actions"""
        results = []
        for action in actions:
            if action['action'] == 'create_issue':
                result = self._create_issue(
                    project=action['project'],
                    summary=action['summary'],
                    description=action.get('description', '')
                )
                # Provide more detail in the success response
                results.append(f"Issue created: {action['project']} - {action['summary']} -> {result}")
            else:
                raise ValueError(f"Unsupported action: {action['action']}")
        return "\n".join(results)

    def _create_issue(self, project: str, summary: str, description: str) -> str:
        """Create JIRA issue with validation"""
        if not any(p.key == project for p in self.jira.projects()):
            raise ValueError(f"Project {project} not found")
            
        if self.dry_run:
            return f"[DRY RUN] Would create issue: {project}-???"
            
        issue = self.jira.create_issue(
            project=project,
            summary=summary,
            description=description,
            issuetype={'name': 'Task'}
        )
        return f"Issue {issue.key} created successfully"

if __name__ == '__main__':
    try:
        agent = JiraAgent()
        print("JIRA Agent Ready (CTRL+C to exit)")
        while True:
            command = input("\nCommand: ")
            if command.lower() in ['exit', 'quit']:
                break
            print(f">> {agent.process_command(command)}")
    except KeyboardInterrupt:
        print("\nSession ended")
    except Exception as e:
        print(f"Fatal Error: {str(e)}")