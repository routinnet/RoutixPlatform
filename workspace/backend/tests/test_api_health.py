"""
Health Check API Tests
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health_check(test_client: TestClient):
    """Test health check endpoint"""
    response = test_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


@pytest.mark.unit
def test_root_endpoint(test_client: TestClient):
    """Test root endpoint returns API info"""
    response = test_client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "Routix Platform"
