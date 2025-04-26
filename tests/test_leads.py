import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import LeadState

TEST_RESUME_CONTENT = b"This is a test resume content"
TEST_RESUME_FILENAME = "test_resume.pdf"

@pytest.fixture
def test_resume_file(tmp_path):
    resume_path = tmp_path / TEST_RESUME_FILENAME
    resume_path.write_bytes(TEST_RESUME_CONTENT)
    return str(resume_path)

def test_create_lead(client: TestClient, test_resume_file):
    with open(test_resume_file, "rb") as f:
        response = client.post(
            "/api/leads",
            data={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com"
            },
            files={"resume": (TEST_RESUME_FILENAME, f, "application/pdf")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert data["state"] == LeadState.PENDING.value
    assert "resume_path" in data
    assert os.path.exists(data["resume_path"])

def test_create_lead_invalid_file_type(client: TestClient, test_resume_file):
    with open(test_resume_file, "rb") as f:
        response = client.post(
            "/api/leads",
            data={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com"
            },
            files={"resume": (TEST_RESUME_FILENAME, f, "invalid/type")}
        )
    
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_list_leads_unauthorized(client: TestClient):
    response = client.get("/api/leads")
    assert response.status_code == 401

def test_list_leads_empty(authorized_client: TestClient):
    response = authorized_client.get("/api/leads")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["has_more"] is False

def test_list_leads_with_data(authorized_client: TestClient, test_resume_file):
    # Create a lead first
    with open(test_resume_file, "rb") as f:
        authorized_client.post(
            "/api/leads",
            data={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com"
            },
            files={"resume": (TEST_RESUME_FILENAME, f, "application/pdf")}
        )
    
    response = authorized_client.get("/api/leads")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["has_more"] is False
    
    lead = data["items"][0]
    assert lead["first_name"] == "John"
    assert lead["last_name"] == "Doe"
    assert lead["email"] == "john.doe@example.com"

def test_update_lead_state(authorized_client: TestClient, test_resume_file):
    # Create a lead first
    with open(test_resume_file, "rb") as f:
        create_response = authorized_client.post(
            "/api/leads",
            data={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com"
            },
            files={"resume": (TEST_RESUME_FILENAME, f, "application/pdf")}
        )
    lead_id = create_response.json()["id"]
    
    # Update the lead state
    response = authorized_client.patch(
        f"/api/leads/{lead_id}",
        json={"state": LeadState.REACHED_OUT.value}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["state"] == LeadState.REACHED_OUT.value

def test_update_lead_not_found(authorized_client: TestClient):
    response = authorized_client.patch(
        "/api/leads/999",
        json={"state": LeadState.REACHED_OUT.value}
    )
    assert response.status_code == 404

def test_download_resume(authorized_client: TestClient, test_resume_file):
    # Create a lead first
    with open(test_resume_file, "rb") as f:
        create_response = authorized_client.post(
            "/api/leads",
            data={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com"
            },
            files={"resume": (TEST_RESUME_FILENAME, f, "application/pdf")}
        )
    lead_id = create_response.json()["id"]
    
    # Download the resume
    response = authorized_client.get(f"/api/leads/{lead_id}/resume")
    assert response.status_code == 200
    assert response.content == TEST_RESUME_CONTENT

def test_download_resume_not_found(authorized_client: TestClient):
    response = authorized_client.get("/api/leads/999/resume")
    assert response.status_code == 404 