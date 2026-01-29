"""Data upload API routes."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.services.data_ingestion import DataIngestionService
from backend.models.dataset import Dataset
from backend.api.schemas.dataset import DatasetResponse

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/", response_model=DatasetResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a data file."""
    try:
        # Read file content
        contents = await file.read()
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Process file
        ingestion_service = DataIngestionService()
        df, metadata, file_path = ingestion_service.process_file(contents, file.filename or "uploaded_file.csv")
        
        # Save to database
        dataset = Dataset(
            filename=metadata["filename"],
            file_path=metadata["file_path"],
            row_count=metadata["row_count"],
            columns=metadata["columns"]
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        return DatasetResponse.from_orm(dataset)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db)
):
    """Get dataset by ID."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DatasetResponse.from_orm(dataset)


@router.get("/", response_model=list[DatasetResponse])
async def list_datasets(db: Session = Depends(get_db)):
    """List all datasets."""
    datasets = db.query(Dataset).all()
    return [DatasetResponse.from_orm(ds) for ds in datasets]

