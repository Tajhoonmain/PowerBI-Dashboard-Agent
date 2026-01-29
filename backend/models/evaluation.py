"""Database models for evaluation results."""
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from backend.database.connection import Base
from datetime import datetime
import json


class EvaluationRecord(Base):
    """Database model for storing evaluation results."""
    __tablename__ = "evaluation_records"
    
    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Task information
    user_command = Column(Text, nullable=False)
    action_type = Column(String, nullable=True)
    success = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Metrics
    latency_ms = Column(Float, default=0.0, nullable=False)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    response_tokens = Column(Integer, default=0, nullable=False)
    estimated_cost = Column(Float, default=0.0, nullable=False)
    action_correctness_score = Column(Float, default=0.0, nullable=False)
    tool_usage_correct = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    llm_provider = Column(String, nullable=True)
    execution_time_ms = Column(Float, default=0.0, nullable=False)
    
    # Full data (JSON)
    intent_parsed = Column(JSON, nullable=True)
    action_generated = Column(JSON, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_command": self.user_command,
            "action_type": self.action_type,
            "success": self.success,
            "error_message": self.error_message,
            "latency_ms": self.latency_ms,
            "prompt_tokens": self.prompt_tokens,
            "response_tokens": self.response_tokens,
            "estimated_cost": self.estimated_cost,
            "action_correctness_score": self.action_correctness_score,
            "tool_usage_correct": self.tool_usage_correct,
            "llm_provider": self.llm_provider,
            "execution_time_ms": self.execution_time_ms,
            "intent_parsed": self.intent_parsed,
            "action_generated": self.action_generated
        }

