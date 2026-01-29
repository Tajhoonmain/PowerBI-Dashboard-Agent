"""Dashboard API schemas."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class ComponentSchema(BaseModel):
    """Dashboard component schema."""
    id: str
    type: str
    title: str
    config: Dict[str, Any]
    position: Dict[str, Any]


class DashboardCreate(BaseModel):
    """Dashboard creation schema."""
    dataset_id: str
    title: str = "Dashboard"
    components: List[Dict[str, Any]]
    layout: Dict[str, Any]


class DashboardUpdate(BaseModel):
    """Dashboard update schema."""
    title: Optional[str] = None
    components: Optional[List[Dict[str, Any]]] = None
    layout: Optional[Dict[str, Any]] = None


class DashboardResponse(BaseModel):
    """Dashboard response schema."""
    id: str
    dataset_id: str
    title: str
    components: List[Dict[str, Any]]
    layout: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True

