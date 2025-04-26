from fastapi import APIRouter
from app.api.endpoints import leads, auth

api_router = APIRouter()

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"]) 