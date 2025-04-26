from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
from app.core.security import get_current_active_user
from app.db import models
from app.db.session import get_db
from app.crud import leads as leads_crud
from app.services.email import send_lead_notification
from app.schemas import Lead, LeadUpdate, PaginatedLeads
import mimetypes
from fastapi.responses import FileResponse

router = APIRouter()

# Configure file upload directory
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Define allowed file types
ALLOWED_RESUME_TYPES = {
    'application/pdf': '.pdf',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'text/plain': '.txt'
}

@router.post("/", response_model=Lead)
async def create_lead(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file type
    content_type = resume.content_type
    if content_type not in ALLOWED_RESUME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types are: {', '.join(ALLOWED_RESUME_TYPES.values())}"
        )

    # Save resume file
    file_location = os.path.join(UPLOAD_DIR, f"{email}_{resume.filename}")
    with open(file_location, "wb+") as file_object:
        file_object.write(await resume.read())

    # Create lead
    lead_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "resume_path": file_location
    }
    db_lead = leads_crud.create_lead(db, lead_data)

    # Send notifications
    try:
        await send_lead_notification(lead_data, "attorney@company.com")
    except Exception as e:
        print(f"[WARN] Email notification failed: {e}")

    return db_lead

@router.get("/", response_model=PaginatedLeads)
async def list_leads(
    page_size: int = 10,
    after_id: Optional[int] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if page_size < 1:
        raise HTTPException(status_code=400, detail="page_size must be greater than 0")
    if page_size > 100:
        page_size = 100
    
    return leads_crud.get_leads(db, page_size, after_id)

@router.get("/{lead_id}/resume")
async def get_resume(
    lead_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    lead = leads_crud.get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if not os.path.exists(lead.resume_path):
        raise HTTPException(status_code=404, detail="Resume file not found")
    
    filename = os.path.basename(lead.resume_path)
    content_type, _ = mimetypes.guess_type(filename)
    if content_type is None:
        content_type = 'application/octet-stream'
    
    return FileResponse(
        path=lead.resume_path,
        filename=filename,
        media_type=content_type
    )

@router.patch("/{lead_id}", response_model=Lead)
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_lead = leads_crud.update_lead(db, lead_id, lead_update.model_dump(exclude_unset=True))
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead 