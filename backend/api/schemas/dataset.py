"""Dataset API schemas."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class ColumnSchema(BaseModel):
    """Column schema."""
    name: str
    type: str
    null_count: int
    null_percentage: float
    unique_count: int
    sample_values: List[Any]


class DatasetCreate(BaseModel):
    """Dataset creation schema."""
    filename: str
    file_path: str
    row_count: int
    columns: List[Dict[str, Any]]


class DatasetResponse(BaseModel):
    """Dataset response schema."""
    id: str
    filename: str
    row_count: int
    columns: List[Dict[str, Any]]
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True

