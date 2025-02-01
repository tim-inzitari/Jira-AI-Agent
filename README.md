# Jira AI Agent 🤖

Natural language interface for Jira task management, powered by AI.

[![Tests](https://github.com/YOUR_USER/jira-ai-agent/actions/workflows/tests.yml/badge.svg)](https://github.com/YOUR_USER/jira-ai-agent/actions)
[![Docker](https://img.shields.io/badge/docker-#230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Jira](https://img.shields.io/badge/jira-#230A0FFF.svg?style=flat&logo=jira&logoColor=white)](https://www.atlassian.com/software/jira)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Features

🤖 Natural language task creation
🔒 Safety validation layers  
🔄 Multiple LLM support (OpenAI, Ollama)
🌐 Web UI + CLI interfaces
✨ Real-time HTMX updates
🧪 Test coverage & mocking

## Installation

1. Clone and setup:
```bash
git clone https://github.com/YOUR_USER/jira-ai-agent.git
cd jira-ai-agent
cp .env.example .env
```

2. Configure environment:
```ini
# Jira Config
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_USER=your-email@domain.com 
JIRA_TOKEN=your-api-token

# LLM Provider
LLM_PROVIDER=openai  # or deepseek, llama
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-3.5-turbo
```

## Usage

### Docker (Recommended)
```bash
# Start all services
docker compose up --build

# CLI only
docker compose run cli
```

Web UI: http://localhost:8000

### Local Development
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python src/web.py  # Web UI
python src/cli.py  # CLI
```

## Testing

Run test suite:
```bash
./scripts/run-tests.sh
```

Configure test env:
```bash
# .env.test
JIRA_SERVER=http://mock-jira
JIRA_USER=test-user 
JIRA_TOKEN=test-token
LLM_PROVIDER=openai
OPENAI_API_KEY=test-api-key
```

Run specific tests:
```bash
pytest tests/test_integration.py::TestJiraIntegration::test_valid_command
pytest --cov=src tests/
```

### Mock Configuration
Test mocks configured in 

conftest.py

:
- OpenAI API responses
- Jira API calls
- Ollama API endpoints

## License

MIT License - See LICENSE file for details
``` 
