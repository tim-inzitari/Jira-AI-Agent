# Jira AI Agent

An AI-powered Jira task management system with Docker deployment

## Features
- Natural language processing for Jira commands
- Docker containerization with monitoring
- Multiple LLM provider support (OpenAI, Ollama)
- Prometheus metrics and Grafana dashboards
- Async API design
- Built-in security features

## Quick Start
git clone https://github.com/yourusername/jira-ai-agent.git
cd jira-ai-agent
cp .env.example .env
docker-compose up -d
# Access at http://localhost:8000

## Configuration
Create .env file:

OLLAMA_HOSTNAME=ollama
OLLAMA_PORT=11434
OLLAMA_HOST=http://ollama:11434

JIRA_SERVER=https://your-domain.atlassian.net
JIRA_USER=your@email.com
JIRA_TOKEN=your_api_token

LLM_PROVIDER=deepseek  # options: deepseek, openai, llama
OPENAI_API_KEY=your_key  # if using OpenAI

## Docker Commands
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Shell access
docker-compose exec web bash

# Run tests
docker-compose exec web pytest

# Stop services
docker-compose down

## API Usage
# Create Jira issue
curl -X POST http://localhost:8000/api/v1/command \
  -H "Content-Type: application/json" \
  -d '{"command": "Create bug ticket for login page"}'

# List projects
curl http://localhost:8000/api/v1/projects

# Health check
curl http://localhost:8000/health

## Monitoring
Prometheus: http://localhost:9090
Grafana: http://localhost:3000 (admin/admin)

## Development
# Local setup without Docker
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
uvicorn src.web.app:app --reload

# Code quality
black src tests
isort src tests
mypy src

## Testing
# Run all tests
pytest

# With coverage
pytest --cov=src

# Single test file
pytest tests/test_core/test_agent.py

## Project Structure
jira-ai-agent/
├── src/              # Source code
├── tests/            # Test suite
├── templates/        # HTML templates
├── static/          # Static assets
├── Dockerfile       # Container definition
├── docker-compose.yml # Services orchestration
├── prometheus.yml   # Metrics config
├── setup.py        # Package config
└── requirements.txt # Dependencies

## Troubleshooting
1. Check container logs: docker-compose logs
2. Verify Ollama connection: curl http://ollama:11434/health
3. Check Jira token: curl -u email:token https://your-domain.atlassian.net/rest/api/2/myself
4. Monitor resource usage: docker stats

## License
MIT License - see LICENSE file for details