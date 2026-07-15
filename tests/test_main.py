import os
import pytest 
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """Remove the temporary test database after tests complete."""
    import time
    
    if os.path.exists("./test_dashboard.db"):
        try:
            os.remove("./test_dashboard.db")
        except OSError:
            pass
            
    yield
   
    try:
        from db_end.db1 import engine
        engine.dispose()
        time.sleep(0.1) # Give OS a moment to release locks
    except Exception:
        pass

    if os.path.exists("./test_dashboard.db"):
        try:
            os.remove("./test_dashboard.db")
        except OSError:
            pass

def test_read_root():
    """Test the root endpoint to ensure the API is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "running",
        "service": "GenAI Invoice Dashboard API"
    }

def test_register_user():
    """Test successful user registration."""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "username": "testuser"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"
    assert "user_id" in response.json()

def test_register_existing_user():
    """Test registering an already existing user."""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "username": "testuser"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_user_success():
    """Test successful user login."""
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"

def test_login_user_invalid_password():
    """Test login with incorrect password."""
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_login_nonexistent_user():
    """Test login for a user that does not exist."""
    response = client.post(
        "/auth/login",
        json={
            "email": "notfound@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
