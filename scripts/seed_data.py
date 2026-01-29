"""Seed sample data into the database."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import init_db, SessionLocal
from backend.models.dataset import Dataset
from backend.services.data_ingestion import DataIngestionService
from backend.services.dashboard_generator import DashboardGenerator
from backend.models.dashboard import Dashboard

def seed_sample_data():
    """Seed the database with sample data."""
    # Initialize database
    init_db()
    
    # Check if sample file exists
    sample_file = "data/examples/sales_data.csv"
    if not os.path.exists(sample_file):
        print(f"Sample file not found: {sample_file}")
        return
    
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Dataset).filter(Dataset.filename == "sales_data.csv").first()
        if existing:
            print("Sample data already exists in database")
            return
        
        # Process sample file
        print(f"Processing sample file: {sample_file}")
        ingestion_service = DataIngestionService()
        
        with open(sample_file, 'rb') as f:
            file_content = f.read()
        
        df, metadata, file_path = ingestion_service.process_file(file_content, "sales_data.csv")
        
        # Save dataset
        dataset = Dataset(
            filename=metadata["filename"],
            file_path=metadata["file_path"],
            row_count=metadata["row_count"],
            columns=metadata["columns"]
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        print(f"✓ Dataset created: {dataset.id}")
        
        # Generate dashboard
        generator = DashboardGenerator()
        dashboard_config = generator.generate_dashboard(df, dataset.columns, "Sample Sales Dashboard")
        
        dashboard = Dashboard(
            dataset_id=dataset.id,
            title=dashboard_config["title"],
            components=dashboard_config["components"],
            layout=dashboard_config["layout"]
        )
        db.add(dashboard)
        db.commit()
        db.refresh(dashboard)
        
        print(f"✓ Dashboard created: {dashboard.id}")
        print("\nSample data seeded successfully!")
        print(f"Dataset ID: {dataset.id}")
        print(f"Dashboard ID: {dashboard.id}")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_data()


