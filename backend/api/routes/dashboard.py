"""Dashboard API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.dataset import Dataset
from backend.models.dashboard import Dashboard
from backend.services.dashboard_generator import DashboardGenerator
from backend.services.data_ingestion import DataIngestionService
from backend.api.schemas.dashboard import (
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.post("/", response_model=DashboardResponse)
async def create_dashboard(
    dashboard: DashboardCreate,
    db: Session = Depends(get_db)
):
    """Create a new dashboard."""
    # Verify dataset exists
    dataset = db.query(Dataset).filter(Dataset.id == dashboard.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Create dashboard
    db_dashboard = Dashboard(
        dataset_id=dashboard.dataset_id,
        title=dashboard.title,
        components=dashboard.components,
        layout=dashboard.layout
    )
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    
    return DashboardResponse.from_orm(db_dashboard)


@router.post("/auto-generate/{dataset_id}", response_model=DashboardResponse)
async def auto_generate_dashboard(
    dataset_id: str,
    title: str = "Dashboard",
    db: Session = Depends(get_db)
):
    """Auto-generate a dashboard from a dataset."""
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data
    ingestion_service = DataIngestionService()
    try:
        df = ingestion_service.load_dataset(dataset.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dataset: {str(e)}")
    
    # Generate dashboard
    generator = DashboardGenerator()
    try:
        dashboard_config = generator.generate_dashboard(df, dataset.columns, title)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Dashboard generation error: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error generating dashboard: {str(e)}")
    
    # Save to database
    try:
        db_dashboard = Dashboard(
            dataset_id=dataset_id,
            title=dashboard_config["title"],
            components=dashboard_config["components"],
            layout=dashboard_config["layout"]
        )
        db.add(db_dashboard)
        db.commit()
        db.refresh(db_dashboard)
        
        return DashboardResponse.from_orm(db_dashboard)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Database save error: {error_trace}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving dashboard: {str(e)}")


@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: str,
    db: Session = Depends(get_db)
):
    """Get dashboard by ID."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return DashboardResponse.from_orm(dashboard)


@router.put("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: str,
    update: DashboardUpdate,
    db: Session = Depends(get_db)
):
    """Update a dashboard."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    if update.title:
        dashboard.title = update.title
    if update.components:
        dashboard.components = update.components
    if update.layout:
        dashboard.layout = update.layout
    
    db.commit()
    db.refresh(dashboard)
    
    return DashboardResponse.from_orm(dashboard)


@router.get("/", response_model=list[DashboardResponse])
async def list_dashboards(db: Session = Depends(get_db)):
    """List all dashboards."""
    dashboards = db.query(Dashboard).all()
    return [DashboardResponse.from_orm(d) for d in dashboards]

