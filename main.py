# main.py
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
from datetime import timedelta
import models
import schemas
import auth
from database import engine, get_db
from email_utils import send_lead_notification
from typing import List

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure file upload directory
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Authentication endpoints
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Lead endpoints
@app.post("/leads/", response_model=schemas.Lead)
async def create_lead(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save the resume file
    file_location = os.path.join(UPLOAD_DIR, f"{email}_{resume.filename}")
    with open(file_location, "wb+") as file_object:
        file_object.write(await resume.read())

    # Create lead in database
    db_lead = models.Lead(
        first_name=first_name,
        last_name=last_name,
        email=email,
        resume_path=file_location
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    # Send notifications
    await send_lead_notification(
        {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "resume_path": file_location
        },
        "attorney@company.com"  # This should be configurable
    )

    return db_lead

@app.get("/leads/", response_model=List[schemas.Lead])
async def list_leads(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    leads = db.query(models.Lead).offset(skip).limit(limit).all()
    return leads

@app.patch("/leads/{lead_id}/state", response_model=schemas.Lead)
async def update_lead_state(
    lead_id: int,
    lead_state: schemas.LeadStateUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db_lead.state = lead_state.state
    db.commit()
    db.refresh(db_lead)
    return db_lead

# User management endpoints
@app.post("/users/", response_model=schemas.User)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

