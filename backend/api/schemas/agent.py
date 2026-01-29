"""AI Agent API schemas."""
from pydantic import BaseModel
from typing import Dict, Any, Optional


class AgentChatRequest(BaseModel):
    """Agent chat request schema."""
    command: str
    dashboard_id: str


class AgentChatResponse(BaseModel):
    """Agent chat response schema."""
    success: bool
    action: Optional[Dict[str, Any]] = None
    explanation: str
    error: Optional[str] = None


