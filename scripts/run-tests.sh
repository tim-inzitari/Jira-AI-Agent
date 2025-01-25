#!/bin/bash

# --- Configuration ---
ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"

# --- Validate Environment ---
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: Missing $ENV_FILE file"
  exit 1
fi

# Load environment variables
set -a  # Auto-export variables
source "$ENV_FILE"
set +a

# --- Validate Ollama Connection ---
if ! curl -s "$OLLAMA_HOST" >/dev/null; then
  echo "Ollama connection failed at $OLLAMA_HOST"
  exit 1
fi

# --- Clean Previous Runs ---
docker-compose -f "$COMPOSE_FILE" down --remove-orphans

# --- Run Tests ---
docker network create jira-net || true
docker-compose -f "$COMPOSE_FILE" build
docker-compose -f "$COMPOSE_FILE" run --rm jira-agent pytest -v tests/

# --- Cleanup ---
TEST_EXIT_CODE=$?
docker-compose -f "$COMPOSE_FILE" down --remove-orphans
exit $TEST_EXIT_CODE