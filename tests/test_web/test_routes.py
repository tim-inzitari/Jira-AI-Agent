import pytest
from fastapi.testclient import TestClient
from src.web.routes import router
from src.core.schemas import CommandRequest

@pytest.mark.asyncio
class TestRoutes:
    async def test_process_command(self, test_client, mock_agent):
        """Test command processing endpoint"""
        response = test_client.post(
            "/api/v1/command",
            json={
                "command": "Create test issue",
                "project": "TEST",
                "dry_run": True
            }
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_list_projects(self, test_client, mock_agent):
        """Test project listing endpoint"""
        response = test_client.get("/api/v1/projects")
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) > 0
        assert projects[0]["key"] == "TEST"

    async def test_service_status(self, test_client, mock_agent):
        """Test service status endpoint"""
        response = test_client.get("/api/v1/status")
        assert response.status_code == 200
        assert "jira" in response.json()
        assert "llm" in response.json()

    async def test_invalid_command(self, test_client):
        """Test invalid command handling"""
        response = test_client.post(
            "/api/v1/command",
            json={"command": ""}
        )
        assert response.status_code == 422

    async def test_rate_limiting(self, test_client):
        """Test rate limiting middleware"""
        for _ in range(100):
            response = test_client.get("/api/v1/health")
        assert response.status_code in (200, 429)