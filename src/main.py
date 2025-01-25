import os
import json
import re
import ollama
from jira import JIRA
from dotenv import load_dotenv
from .schemas import validate_action

load_dotenv()

DEEPSEEK_SYSTEM_PROMPT = """<think>
You are a JIRA assistant. Structure responses as:
1. XML-style reasoning within <think> tags
2. Executable JSON command within <answer> tags

Response Template:
{
  "reasoning": "<think>[Your analysis steps]</think>",
  "answer": "<answer>{\\"action\\":\\"create_issue\\",\\"project\\":\\"PROJ\\",\\"summary\\":\\"Task Name\\"}</answer>"
}
</think>"""

class JiraAgent:
    def __init__(self):
        self._init_jira()
        self._init_llm()

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
            # Verify connection
            _ = self.jira.projects()
        except Exception as e:
            raise ConnectionError(f"JIRA connection failed: {str(e)}")
        
    def _init_llm(self):
        """Initialize Ollama client with model check"""
        self.llm = ollama.Client(host=os.getenv('OLLAMA_HOST'))
        try:
            models = self.llm.list()
            
            # Debug: Print available models
            print("Available models:", [m["model"] for m in models["models"]])
            
            # Case-insensitive check
            if not any(m["model"].lower() == "deepseek-r1:14b" for m in models["models"]):
                raise ValueError("deepseek-r1:14b model not available")
        except Exception as e:
            raise ConnectionError(f"Ollama connection failed: {str(e)}")

    def process_command(self, command: str) -> str:
        """Process user command with validation pipeline"""
        try:
            # Get LLM response
            response = self.llm.chat(
                model='deepseek-r1:14b',
                messages=[
                    {"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT},
                    {"role": "user", "content": command}
                ]
            )
            
            # Parse and validate
            response_data = self._parse_response(response)
            action = self._extract_action(response_data)
            
            # Execute and return
            return self._execute_action(action)
            
        except json.JSONDecodeError:
            return "Error: Invalid JSON response format"
        except ValueError as ve:
            return f"Validation Error: {str(ve)}"
        except Exception as e:
            return f"System Error: {str(e)}"

    def _parse_response(self, response: dict) -> dict:
        """Parse and validate response structure"""
        try:
            response_data = json.loads(response['message']['content'])
            
            # Debug: Print raw response
            print("Raw response:", response['message']['content'])
            
            # Validate required fields
            required_keys = ['reasoning', 'answer']
            if not all(key in response_data for key in required_keys):
                raise ValueError("Missing required response fields")
                
            # Validate XML tags
            if not re.search(r'<answer>.*</answer>', response_data['answer']):
                raise ValueError("Missing answer XML tags")
                
            return response_data
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON structure in LLM response")

    def _extract_action(self, response_data: dict) -> dict:
        """Extract and validate action from answer tags"""
        answer_content = re.search(
            r'<answer>(.*?)</answer>',
            response_data['answer'],
            re.DOTALL
        ).group(1)
        
        # Clean and parse JSON
        try:
            return json.loads(
                answer_content
                .replace("'", '"')  # Handle single quotes
                .replace('\n', '')  # Remove newlines
            )
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in answer content")

    def _execute_action(self, action: dict) -> str:
        """Execute validated JIRA action"""
        validate_action(action)  # Add this line
        
        if action['action'] == 'create_issue':
            return self._create_issue(
                project=action['project'],
                summary=action['summary'],
                description=action.get('description', '')
            )
        
        raise ValueError(f"Unsupported action: {action['action']}")

    def _create_issue(self, project: str, summary: str, description: str) -> str:
        """Create JIRA issue with validation"""
        # Verify project exists
        if not any(p.key == project for p in self.jira.projects()):
            raise ValueError(f"Project {project} not found")
            
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