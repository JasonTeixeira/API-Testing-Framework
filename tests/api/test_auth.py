"""
Authentication API Tests
Comprehensive tests for authentication endpoints
"""

import pytest
from framework.clients.api_client import APIClient


@pytest.mark.smoke
class TestAuthentication:
    """Test suite for authentication flows."""
    
    def test_register_new_user(self, api_client):
        """Test user registration with valid data."""
        response = api_client.post("/api/v1/auth/register", json={
            "username": "newuser123",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser123"
        assert data["email"] == "newuser@example.com"
        assert "hashed_password" not in data
    
    def test_login_success(self, api_client):
        """Test successful login with valid credentials."""
        token_data = api_client.login("testuser", "Test123!")
        
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert api_client.token is not None
    
    def test_login_invalid_credentials(self, api_client):
        """Test login fails with invalid credentials."""
        with pytest.raises(Exception):
            api_client.login("invalid_user", "wrong_password")
    
    def test_get_current_user(self, authenticated_client):
        """Test get current user info after authentication."""
        response = authenticated_client.get("/api/v1/users/me")
        
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data


@pytest.fixture
def api_client():
    """Provide API client instance."""
    client = APIClient(base_url="http://localhost:8000")
    yield client
    client.close()


@pytest.fixture
def authenticated_client(api_client):
    """Provide authenticated API client."""
    api_client.login("testuser", "Test123!")
    return api_client
