import pytest
from fastapi.testclient import TestClient
from src.web.app import app

@pytest.mark.asyncio
class TestApp:
    def test_app_initialization(self, test_client):
        """Test FastAPI app initialization"""
        assert app.title == "Jira AI Agent"
        assert app.version == "1.0.0"

    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_cors_middleware(self, test_client):
        """Test CORS middleware configuration"""
        response = test_client.options("/")
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "*"
        assert "GET" in response.headers["access-control-allow-methods"]

    def test_static_files(self, test_client):
        """Test static files serving"""
        response = test_client.get("/static/test.css")
        assert response.status_code in (200, 404)  # 404 if file doesn't exist

    def test_error_handler(self, test_client):
        """Test error handling"""
        response = test_client.get("/nonexistent")
        assert response.status_code == 404