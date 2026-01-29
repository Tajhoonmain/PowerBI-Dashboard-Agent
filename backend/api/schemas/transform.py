"""Transformation API schemas."""
from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class TransformationStepCreate(BaseModel):
    """Transformation step creation schema."""
    dataset_id: str
    step_type: str  # cast, filter, rename, remove_nulls, aggregate
    parameters: Dict[str, Any]
    order: int


class TransformationStepResponse(BaseModel):
    """Transformation step response schema."""
    id: str
    dataset_id: str
    step_type: str
    parameters: Dict[str, Any]
    order: int
    
    class Config:
        from_attributes = True
        populate_by_name = True


class ApplyTransformationsRequest(BaseModel):
    """Request to apply transformations."""
    dataset_id: str
    steps: List[Dict[str, Any]]

