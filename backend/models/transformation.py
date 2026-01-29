"""Transformation step database model."""
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from backend.database.connection import Base
import uuid


class TransformationStep(Base):
    """Transformation step model for storing data transformation history."""
    
    __tablename__ = "transformation_steps"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    step_type = Column(String, nullable=False)  # cast, filter, rename, remove_nulls, aggregate
    parameters = Column(JSON, nullable=False)  # Step-specific parameters
    order = Column(Integer, nullable=False)  # Order of application
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "step_type": self.step_type,
            "parameters": self.parameters,
            "order": self.order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


