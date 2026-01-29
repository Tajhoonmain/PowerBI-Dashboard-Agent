"""AI Agent API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.dashboard import Dashboard
from backend.models.dataset import Dataset
from backend.services.dashboard_generator import DashboardGenerator
from ai_agent.agent import DashboardAgent
from backend.api.schemas.agent import AgentChatRequest, AgentChatResponse

router = APIRouter(prefix="/api/agent", tags=["agent"])

# Global agent instance
agent = DashboardAgent()


@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_agent(
    request: AgentChatRequest,
    db: Session = Depends(get_db)
):
    """Chat with AI agent to modify dashboard."""
    # Get dashboard
    dashboard = db.query(Dashboard).filter(Dashboard.id == request.dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Get dataset for column info
    dataset = db.query(Dataset).filter(Dataset.id == dashboard.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Convert dashboard to dict
    dashboard_dict = {
        "id": dashboard.id,
        "components": dashboard.components,
        "layout": dashboard.layout
    }
    
    # Process command with full column metadata
    try:
        result = agent.process_command(
            request.command,
            dashboard_dict,
            dataset.columns  # Full column metadata, not just names
        )
        
        # Apply action if successful
        if result.get("success"):
            generator = DashboardGenerator()
            
            action = result.get("action")
            if action == "add_component":
                component = result.get("component")
                if component:
                    dashboard_dict = generator.add_component(
                        dashboard_dict,
                        component
                    )
            elif action == "update_component":
                component_id = result.get("component_id")
                updates = result.get("updates", {})
                if component_id and updates:
                    dashboard_dict = generator.update_component(
                        dashboard_dict,
                        component_id,
                        updates
                    )
            elif action == "remove_component":
                component_id = result.get("component_id")
                if component_id:
                    dashboard_dict = generator.remove_component(
                        dashboard_dict,
                        component_id
                    )
            elif action == "apply_filter":
                # Filter actions need to reload data and regenerate affected components
                # This is a more complex operation - for now, return success
                # TODO: Implement full filter application
                pass
            
            # Update database with new state
            dashboard.components = dashboard_dict["components"]
            dashboard.layout = dashboard_dict["layout"]
            db.commit()
            db.refresh(dashboard)
        
        return AgentChatResponse(
            success=result.get("success", False),
            action=result,
            explanation=result.get("explanation", "Action completed"),
            error=result.get("error")
        )
        
    except Exception as e:
        return AgentChatResponse(
            success=False,
            explanation=f"Error processing command: {str(e)}",
            error=str(e)
        )

