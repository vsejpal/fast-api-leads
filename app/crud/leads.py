from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.db import models
from app.schemas import PaginatedLeads

def create_lead(db: Session, lead_data: Dict[str, Any]) -> models.Lead:
    db_lead = models.Lead(**lead_data)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def get_leads(
    db: Session,
    page_size: int = 10,
    after_id: Optional[int] = None
) -> PaginatedLeads:
    query = db.query(models.Lead)
    total = query.count()

    if after_id:
        query = query.filter(models.Lead.id > after_id)
    
    items = query.order_by(models.Lead.id).limit(page_size + 1).all()
    
    has_more = len(items) > page_size
    if has_more:
        items = items[:-1]

    last_id = items[-1].id if items else None

    return PaginatedLeads(
        items=items,
        total=total,
        has_more=has_more,
        last_id=last_id
    )

def get_lead(db: Session, lead_id: int) -> Optional[models.Lead]:
    return db.query(models.Lead).filter(models.Lead.id == lead_id).first()

def update_lead(
    db: Session,
    lead_id: int,
    lead_data: Dict[str, Any]
) -> Optional[models.Lead]:
    db_lead = get_lead(db, lead_id)
    if db_lead:
        for field, value in lead_data.items():
            setattr(db_lead, field, value)
        db.commit()
        db.refresh(db_lead)
    return db_lead 