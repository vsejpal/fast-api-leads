from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_user(client: TestClient):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert data["is_active"] is True

def test_create_user_duplicate_email(client: TestClient, test_user):
    response = client.post(
        "/api/auth/register",
        json={
            "email": test_user["email"],
            "password": "anotherpassword123"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client: TestClient, test_user):
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, test_user):
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user["email"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_wrong_email(client: TestClient):
    response = client.post(
        "/api/auth/token",
        data={
            "username": "nonexistent@example.com",
            "password": "somepassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password" 