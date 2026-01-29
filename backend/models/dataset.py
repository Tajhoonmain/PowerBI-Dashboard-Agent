"""Dataset database model."""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func
from backend.database.connection import Base
import uuid


class Dataset(Base):
    """Dataset model for storing uploaded data metadata."""
    
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    row_count = Column(Integer, nullable=False)
    columns = Column(JSON, nullable=False)  # List of column metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "row_count": self.row_count,
            "columns": self.columns,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


