from sqlalchemy.orm import Session
import pytest
from app.crud import leads as leads_crud
from app.crud import users as users_crud
from app.db.models import LeadState

def test_create_user(db: Session):
    email = "test@example.com"
    password = "testpassword123"
    user = users_crud.create_user(db, email, password)
    assert user.email == email
    assert user.hashed_password != password  # Password should be hashed
    assert user.is_active is True

def test_get_user_by_email(db: Session):
    email = "test@example.com"
    password = "testpassword123"
    created_user = users_crud.create_user(db, email, password)
    
    user = users_crud.get_user_by_email(db, email)
    assert user.id == created_user.id
    assert user.email == email

def test_get_user_by_email_not_found(db: Session):
    user = users_crud.get_user_by_email(db, "nonexistent@example.com")
    assert user is None

def test_create_lead(db: Session):
    lead_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "resume_path": "/path/to/resume.pdf"
    }
    lead = leads_crud.create_lead(db, lead_data)
    assert lead.first_name == lead_data["first_name"]
    assert lead.last_name == lead_data["last_name"]
    assert lead.email == lead_data["email"]
    assert lead.resume_path == lead_data["resume_path"]
    assert lead.state == LeadState.PENDING

def test_get_lead(db: Session):
    # Create a lead first
    lead_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "resume_path": "/path/to/resume.pdf"
    }
    created_lead = leads_crud.create_lead(db, lead_data)
    
    # Get the lead
    lead = leads_crud.get_lead(db, created_lead.id)
    assert lead.id == created_lead.id
    assert lead.first_name == lead_data["first_name"]
    assert lead.last_name == lead_data["last_name"]
    assert lead.email == lead_data["email"]

def test_get_lead_not_found(db: Session):
    lead = leads_crud.get_lead(db, 999)
    assert lead is None

def test_get_leads_empty(db: Session):
    leads = leads_crud.get_leads(db, 10)
    assert leads.items == []
    assert leads.total == 0
    assert leads.has_more is False

def test_get_leads_pagination(db: Session):
    # Create multiple leads
    for i in range(15):
        lead_data = {
            "first_name": f"User{i}",
            "last_name": "Test",
            "email": f"user{i}@example.com",
            "resume_path": f"/path/to/resume{i}.pdf"
        }
        leads_crud.create_lead(db, lead_data)
    
    # Get first page
    page_size = 10
    result = leads_crud.get_leads(db, page_size)
    assert len(result.items) == page_size
    assert result.total == 15
    assert result.has_more is True
    
    # Get second page
    last_id = result.items[-1].id
    result2 = leads_crud.get_leads(db, page_size, after_id=last_id)
    assert len(result2.items) == 5
    assert result2.total == 15
    assert result2.has_more is False

def test_update_lead(db: Session):
    # Create a lead first
    lead_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "resume_path": "/path/to/resume.pdf"
    }
    created_lead = leads_crud.create_lead(db, lead_data)
    
    # Update the lead
    update_data = {
        "first_name": "Jane",
        "state": LeadState.REACHED_OUT
    }
    updated_lead = leads_crud.update_lead(db, created_lead.id, update_data)
    
    assert updated_lead.id == created_lead.id
    assert updated_lead.first_name == update_data["first_name"]
    assert updated_lead.last_name == lead_data["last_name"]  # Unchanged
    assert updated_lead.state == LeadState.REACHED_OUT

def test_update_lead_not_found(db: Session):
    update_data = {"first_name": "Jane"}
    updated_lead = leads_crud.update_lead(db, 999, update_data)
    assert updated_lead is None 