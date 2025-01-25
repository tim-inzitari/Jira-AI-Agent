.PHONY: test test-unit test-integration clean

# Default test target
test: test-unit test-integration

# Unit tests (mocked)
test-unit:
	docker-compose -f docker-compose.test.yml run --rm tester pytest -v tests/ -m "not integration"

# Integration tests (real services)
test-integration:
	docker-compose -f docker-compose.test.yml up -d ollama
	docker-compose -f docker-compose.test.yml run --rm tester pytest -v tests/ -m integration

# Full CI pipeline
ci: clean build test

# Cleanup
clean:
	docker-compose -f docker-compose.test.yml down -v --remove-orphans

# Build test environment
build:
	docker-compose -f docker-compose.test.yml build

# Run specific test
test-%:
	docker-compose -f docker-compose.test.yml run --rm tester pytest -v tests/test_$*.py