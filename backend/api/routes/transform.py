"""Transformation API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.dataset import Dataset
from backend.models.transformation import TransformationStep
from backend.services.transformation import TransformationService
from backend.services.data_ingestion import DataIngestionService
from backend.api.schemas.transform import (
    TransformationStepCreate,
    TransformationStepResponse,
    ApplyTransformationsRequest
)
import pandas as pd

router = APIRouter(prefix="/api/transform", tags=["transform"])


@router.post("/apply", response_model=dict)
async def apply_transformations(
    request: ApplyTransformationsRequest,
    db: Session = Depends(get_db)
):
    """Apply transformations to a dataset."""
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data
    ingestion_service = DataIngestionService()
    df = ingestion_service.load_dataset(dataset.file_path)
    
    # Apply transformations
    transform_service = TransformationService()
    transformed_df = transform_service.apply_transformations(df, request.steps)
    
    # Convert to records for response
    return {
        "dataset_id": request.dataset_id,
        "row_count": len(transformed_df),
        "columns": list(transformed_df.columns),
        "data": transformed_df.head(100).to_dict('records')
    }


@router.post("/steps", response_model=TransformationStepResponse)
async def create_transformation_step(
    step: TransformationStepCreate,
    db: Session = Depends(get_db)
):
    """Create a transformation step."""
    # Verify dataset exists
    dataset = db.query(Dataset).filter(Dataset.id == step.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Create step
    db_step = TransformationStep(
        dataset_id=step.dataset_id,
        step_type=step.step_type,
        parameters=step.parameters,
        order=step.order
    )
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    
    return TransformationStepResponse.from_orm(db_step)


@router.get("/steps/{dataset_id}", response_model=list[TransformationStepResponse])
async def get_transformation_steps(
    dataset_id: str,
    db: Session = Depends(get_db)
):
    """Get all transformation steps for a dataset."""
    steps = db.query(TransformationStep).filter(
        TransformationStep.dataset_id == dataset_id
    ).order_by(TransformationStep.order).all()
    
    return [TransformationStepResponse.from_orm(step) for step in steps]


