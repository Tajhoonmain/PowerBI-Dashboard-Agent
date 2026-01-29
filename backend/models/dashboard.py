"""Dashboard database model."""
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from backend.database.connection import Base
import uuid


class Dashboard(Base):
    """Dashboard model for storing dashboard configurations."""
    
    __tablename__ = "dashboards"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    title = Column(String, nullable=False, default="Dashboard")
    components = Column(JSON, nullable=False)  # List of dashboard components
    layout = Column(JSON, nullable=False)  # Layout configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "title": self.title,
            "components": self.components,
            "layout": self.layout,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


