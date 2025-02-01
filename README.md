# Jira AI Agent 🤖📋

An AI-powered interface for Jira task management via natural language commands.

[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker)]
[![Jira](https://img.shields.io/badge/Jira-Integrated-0052CC?logo=jira)]
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)]

# Features
- Web interface (FastAPI + HTMX)
- CLI version for terminal use
- Natural language processing via Ollama
- Jira API integration
- Safety validation layers
- Dry-run testing mode

# Quick Start
1. Clone repo:
git clone https://github.com/YOUR_USER/jira-ai-agent.git
cd jira-ai-agent

2. Configure environment:
cp .env.example .env
nano .env  # Edit credentials

3. Start services:
docker-compose up --build web

# Web Interface
Access at: http://localhost:8000
- Type commands in textbox
- Real-time responses
- Error highlighting

# CLI Usage
docker-compose run --rm cli
Example: "Create task in TEST: Update docs"

## Configuration (.env)

Ensure that your .env file includes the new variables:

  • LLM_PROVIDER – Set to one of: deepseek, openai, or llama  
  • OPENAI_API_KEY – Provide your OpenAI API key when using the OpenAI provider

Example:

OLLAMA_HOST=http://YOUR_OLLAMA_IP:11434
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_USER=your@email.com
JIRA_TOKEN=your_api_token
DRY_RUN=false

# Troubleshooting
- Clean rebuild: docker-compose down --remove-orphans && docker-compose build --no-cache
- Test connections: curl $OLLAMA_HOST/api/tags
- Check logs: docker-compose logs web

# Roadmap
- [x] Web interface
- [x] Multi-step commands
- [ ] User authentication
- [ ] Slack integration

# License
MIT License - Use at your own risk
