# Jira AI Agent 🤖📋

An AI-powered agent that creates Jira tasks using natural language commands via Ollama LLMs.

[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker)](https://www.docker.com)

[![Jira](https://img.shields.io/badge/Jira-Integration-0052CC?logo=jira)](https://www.atlassian.com/software/jira)

# Features ✨

- 🗣️ Natural language to Jira task creation

- 🔌 Integration with Ollama LLMs (supports Deepseek-r1 models)

- 🔒 Safety checks and command validation

- 🧪 Dry-run mode for testing

- 🛠️ JSON schema validation for AI responses

- 🐳 Docker container support

- ✅ Integration testing framework

# Prerequisites 📋

- Docker and Docker Compose

- Jira instance with API access

- Ollama server (local or remote)

- Python 3.11+ (for development)

# Installation 🚀

```

git clone https://github.com/yourusername/jira-ai-agent.git

cd jira-ai-agent

cp .env.example .env

nano .env  # Edit with your credentials

```

# Configuration ⚙️

```

# .env

OLLAMA_HOST=http://your-ollama-server:11434

JIRA_SERVER=https://your-domain.atlassian.net

JIRA_USER=your@email.com

JIRA_TOKEN=your_api_token

DRY_RUN=false  # Set to true for testing

```

# Usage 📦

```

# Run interactive mode

docker-compose build

docker-compose run --rm jira-agent python src/main.py

# Example commands:

# Create issue: "Create urgent task in project TEST to update documentation"

# List projects: "Show available projects in TEST"

```

# Safety Measures 🔒

- Command blacklisting (delete/drop/admin)

- Project whitelisting

- JSON schema validation

- Input sanitization

- Rate limiting (coming soon)

# Roadmap 🗺️

- [ ] Support for issue comments

- [ ] Multi-step task creation

- [ ] Web interface

- [ ] Advanced error recovery

# Troubleshooting 🐞

```

# Connection tests

curl $OLLAMA_HOST/api/tags

curl -u $JIRA_USER:$JIRA_TOKEN $JIRA_SERVER/rest/api/2/myself

# Clean rebuild

docker system prune -a

docker-compose build --no-cache

```

# License 📄

MIT License - See [LICENSE](LICENSE)

---

**Disclaimer**: Use at your own risk. Always test in a non-production environment first.

```