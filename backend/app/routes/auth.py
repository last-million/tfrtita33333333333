from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class OAuthCredentials(BaseModel):
    service: str  # 'supabase', 'google', 'airtable', etc.
    access_token: str
    refresh_token: Optional[str] = None

@router.post("/connect")
async def connect_service(credentials: OAuthCredentials):
    """
    Handle OAuth token management for different services.
    Supports Supabase, Google, Airtable, etc.
    """
    # Validate and store OAuth tokens securely
    # Implement service-specific token validation
    return {
        "status": "connected", 
        "service": credentials.service,
        "message": "Service successfully authenticated"
    }

@router.get("/services")
async def list_connected_services():
    """
    Retrieve list of currently connected services
    """
    # Implement logic to fetch connected services from database or session
    return {
        "services": [
            {"name": "supabase", "connected": True},
            {"name": "google", "connected": False},
            {"name": "airtable", "connected": True}
        ]
    }
