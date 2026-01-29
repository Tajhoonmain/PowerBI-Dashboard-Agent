"""API routes for Tempo frontend integration."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.dataset import Dataset
from backend.models.dashboard import Dashboard
from backend.services.data_ingestion import DataIngestionService
from backend.services.dashboard_generator import DashboardGenerator
from ai_agent.agent import DashboardAgent
from typing import List, Dict, Any
from pydantic import BaseModel
import json
import pandas as pd

router = APIRouter(prefix="/api/v1", tags=["frontend"])

# Global agent instance
agent = DashboardAgent()


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working."""
    return {"status": "ok", "message": "API is working"}


@router.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Test upload endpoint to verify file upload works."""
    try:
        contents = await file.read()
        return {
            "status": "ok",
            "filename": file.filename,
            "size": len(contents),
            "content_type": file.content_type
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


class AICommandRequest(BaseModel):
    """Request model for AI command processing."""
    command: str
    state: Dict[str, Any]


@router.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload dataset - returns format matching Tempo frontend."""
    import traceback
    try:
        # Check filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        print(f"[UPLOAD] Received file: {file.filename}, content_type: {file.content_type}")
        print(f"[UPLOAD] File object: {file}")
        print(f"[UPLOAD] File size attribute: {getattr(file, 'size', 'unknown')}")
        
        # Read file contents
        contents = await file.read()
        print(f"[UPLOAD] Read contents: {len(contents)} bytes")
        print(f"[UPLOAD] First 100 bytes (hex): {contents[:100].hex() if len(contents) > 0 else 'EMPTY'}")
        print(f"[UPLOAD] First 100 bytes (text): {contents[:100] if len(contents) > 0 else 'EMPTY'}")
        
        if len(contents) == 0:
            print("[UPLOAD ERROR] File contents are 0 bytes after reading")
            raise HTTPException(status_code=400, detail="File is empty (0 bytes). Please check your file and try again.")
        
        # Process file
        print(f"[UPLOAD] Processing file...")
        ingestion_service = DataIngestionService()
        df, metadata, file_path = ingestion_service.process_file(
            contents, file.filename
        )
        print(f"[UPLOAD] Processed: {len(df)} rows, {len(df.columns)} columns")
        
        # Check if DataFrame is empty (no rows)
        if df.empty:
            raise HTTPException(
                status_code=400, 
                detail="File contains no data rows. Please ensure your CSV has a header row and at least one data row."
            )
        
        # Check if DataFrame has no columns
        if len(df.columns) == 0:
            raise HTTPException(
                status_code=400,
                detail="File contains no columns. Please check your file format."
            )
        
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
        
        # Convert to frontend format
        # Map column types: 'numeric' -> 'number', 'string' -> 'string', 'date' -> 'date'
        frontend_columns = []
        for col in dataset.columns:
            col_type = col.get('type', 'string')
            if col_type == 'numeric':
                col_type = 'number'
            elif col_type not in ['string', 'date', 'boolean']:
                col_type = 'string'
            
            frontend_columns.append({
                "name": col.get('name', ''),
                "type": col_type,
                "confidence": 0.95  # High confidence from our detection
            })
        
        # Get sample data (first 100 rows)
        sample_data = df.head(100).to_dict('records')
        # Convert to JSON-serializable format
        for record in sample_data:
            for key, value in record.items():
                if hasattr(value, 'isoformat'):  # datetime
                    record[key] = value.isoformat()
                elif hasattr(value, '__float__'):  # numpy types
                    try:
                        record[key] = float(value) if not pd.isna(value) else None
                    except:
                        record[key] = str(value)
        
        return {
            "id": dataset.id,
            "name": dataset.filename.replace('.csv', '').replace('.xlsx', ''),
            "data": sample_data,
            "columns": frontend_columns,
            "rowCount": dataset.row_count,
            "uploadedAt": dataset.created_at.isoformat() if dataset.created_at else None
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[UPLOAD ERROR] {str(e)}")
        print(f"[UPLOAD ERROR TRACE] {error_trace}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/ai/process")
async def process_ai_command(
    request: AICommandRequest,
    db: Session = Depends(get_db)
):
    """
    Process AI command - returns format matching Tempo frontend.
    
    Expected input:
    {
        "command": "user command string",
        "state": {
            "datasets": [...],
            "widgets": [...]
        }
    }
    """
    try:
        user_command = request.command
        frontend_state = request.state
        
        if not user_command:
            raise HTTPException(status_code=400, detail="Command is required")
        
        # Get first dataset from frontend state
        datasets = frontend_state.get("datasets", [])
        if not datasets:
            return {
                "message": "Please upload a dataset first.",
                "json": None,
                "widgets": None
            }
        
        frontend_dataset = datasets[0]
        
        # Find or create dataset in backend
        dataset_id = frontend_dataset.get("id")
        if dataset_id:
            # Try to find in database
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                # Dataset might be client-side only, create a minimal one
                # For now, we'll work with the frontend dataset structure
                pass
        
        # Convert frontend state to backend format
        backend_widgets = frontend_state.get("widgets", [])
        dashboard_dict = {
            "id": "temp",
            "components": [convert_frontend_widget_to_backend(w) for w in backend_widgets],
            "layout": {"rows": 12, "cols": 12, "grid": []}
        }
        
        # Convert frontend columns to backend format with sample values
        backend_columns = []
        dataset_data = frontend_dataset.get("data", [])
        
        for col in frontend_dataset.get("columns", []):
            col_type = col.get("type", "string")
            if col_type == "number":
                col_type = "numeric"
            
            col_name = col.get("name", "")
            # Extract sample values from dataset data
            sample_values = []
            if dataset_data:
                for row in dataset_data[:5]:  # First 5 rows
                    if col_name in row and row[col_name] is not None:
                        sample_values.append(str(row[col_name]))
            
            backend_columns.append({
                "name": col_name,
                "type": col_type,
                "sample_values": sample_values[:3]  # Limit to 3 samples
            })
        
        # Process command with agent (include dataset data for analysis)
        import time
        import uuid
        from backend.services.evaluation import evaluator
        from backend.config import settings
        
        task_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Start evaluation tracking
        evaluator.start_evaluation(task_id, user_command)
        
        try:
            dataset_data = frontend_dataset.get("data", [])
            result = agent.process_command(
                user_command,
                dashboard_dict,
                backend_columns,
                dataset_data=dataset_data  # Pass data for explain_chart analysis
            )
            
            # Get intent from agent (if available)
            intent = getattr(agent, 'last_intent', {})
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Record evaluation
            eval_result = evaluator.complete_evaluation(
                user_command=user_command,
                intent=intent,
                action=result,
                success=result.get("success", False),
                error_message=result.get("error") if not result.get("success") else None,
                llm_provider=settings.llm_provider
            )
            
            # Override with actual latency
            eval_result.latency_ms = latency_ms
            eval_result.execution_time_ms = latency_ms
            
            # Save to database (with error handling)
            try:
                from backend.models.evaluation import EvaluationRecord
                eval_record = EvaluationRecord(
                    id=str(uuid.uuid4()),
                    task_id=eval_result.task_id,
                    timestamp=eval_result.timestamp,
                    user_command=eval_result.user_command,
                    action_type=eval_result.action_type,
                    success=eval_result.success,
                    error_message=eval_result.error_message,
                    latency_ms=eval_result.latency_ms,
                    prompt_tokens=eval_result.prompt_tokens,
                    response_tokens=eval_result.response_tokens,
                    estimated_cost=eval_result.estimated_cost,
                    action_correctness_score=eval_result.action_correctness_score,
                    tool_usage_correct=eval_result.tool_usage_correct,
                    llm_provider=eval_result.llm_provider,
                    execution_time_ms=eval_result.execution_time_ms,
                    intent_parsed=eval_result.intent_parsed,
                    action_generated=eval_result.action_generated
                )
                db.add(eval_record)
                db.commit()
            except Exception as db_error:
                # Rollback on error and continue (evaluation is optional)
                db.rollback()
                print(f"Warning: Failed to save evaluation record: {db_error}")
                # Try to create table if it doesn't exist
                try:
                    from backend.database.connection import init_db
                    init_db()
                    print("Database tables reinitialized")
                except Exception as init_error:
                    print(f"Warning: Could not reinitialize database: {init_error}")
            
            # Convert result to frontend format
            widgets = []
            if result.get("success"):
                action = result.get("action")
                
                if action == "add_multiple_components":
                    # Handle full dashboard generation
                    components = result.get("components", [])
                    for component in components:
                        widgets.append(convert_backend_component_to_frontend(
                            component,
                            frontend_dataset.get("id", "")
                        ))
                elif action == "add_component":
                    component = result.get("component")
                    if component:
                        widgets.append(convert_backend_component_to_frontend(
                            component, 
                            frontend_dataset.get("id", "")
                        ))
                elif action == "explain_chart":
                    # Return explanation for chart analysis - only text, no JSON
                    explanation_text = result.get("explanation", "Chart explanation")
                    return {
                        "message": explanation_text,  # Clean explanation text only
                        "json": None,  # Don't include JSON for explanations
                        "widgets": None,
                        "explanation": {
                            "chart_id": result.get("chart_id"),
                            "insights": explanation_text,
                            "question": result.get("question")
                        }
                    }
                elif action == "answer_question":
                    # Return answer to data question - only text, no JSON
                    answer_text = result.get("explanation", "Answer to question")
                    return {
                        "message": answer_text,  # Clean answer text only
                        "json": None,  # Don't include JSON for Q&A
                        "widgets": None,
                        "explanation": {
                            "question": result.get("question"),
                            "answer": answer_text
                        }
                    }
                elif action == "update_component":
                    # For updates, we need to find the existing widget and update it
                    component_id = result.get("component_id")
                    updates = result.get("updates", {})
                    # Return update info - frontend will handle the update
                    return {
                        "message": result.get("explanation", "Component updated"),
                        "json": result,
                        "widgets": None,  # Frontend handles updates differently
                        "update": {
                            "id": component_id,
                            "updates": updates
                        }
                    }
                elif action == "remove_component":
                    # Return remove info
                    return {
                        "message": result.get("explanation", "Component removed"),
                        "json": result,
                        "widgets": None,
                        "remove": {
                            "id": result.get("component_id")
                        }
                    }
            
            return {
                "message": result.get("explanation", "Action completed"),
                "json": result,
                "widgets": widgets if widgets else None
            }
        except Exception as agent_error:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Agent error: {error_trace}")
            
            # Record failed evaluation
            latency_ms = (time.time() - start_time) * 1000
            eval_result = evaluator.complete_evaluation(
                user_command=user_command,
                intent=getattr(agent, 'last_intent', {}),
                action={"success": False, "error": str(agent_error)},
                success=False,
                error_message=str(agent_error),
                llm_provider=settings.llm_provider
            )
            eval_result.latency_ms = latency_ms
            
            # Save to database (with error handling)
            try:
                from backend.models.evaluation import EvaluationRecord
                eval_record = EvaluationRecord(
                    id=str(uuid.uuid4()),
                    task_id=eval_result.task_id,
                    timestamp=eval_result.timestamp,
                    user_command=eval_result.user_command,
                    action_type=eval_result.action_type,
                    success=False,
                    error_message=str(agent_error),
                    latency_ms=latency_ms,
                    prompt_tokens=0,
                    response_tokens=0,
                    estimated_cost=0.0,
                    action_correctness_score=0.0,
                    tool_usage_correct=False,
                    llm_provider=settings.llm_provider,
                    execution_time_ms=latency_ms,
                    intent_parsed=getattr(agent, 'last_intent', {}),
                    action_generated={"error": str(agent_error)}
                )
                db.add(eval_record)
                db.commit()
            except Exception as db_error:
                db.rollback()
                print(f"Warning: Failed to save evaluation record: {db_error}")
            
            return {
                "message": f"Error processing command: {str(agent_error)}",
                "json": None,
                "widgets": None
            }
            
    except Exception as e:
        # Record evaluation for outer exception
        try:
            latency_ms = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0.0
            eval_result = evaluator.complete_evaluation(
                user_command=user_command if 'user_command' in locals() else "",
                intent={},
                action={"success": False, "error": str(e)},
                success=False,
                error_message=str(e),
                llm_provider=settings.llm_provider
            )
        except:
            pass  # Don't fail if evaluation recording fails
        
        return {
            "message": f"Error processing command: {str(e)}",
            "json": None,
            "widgets": None
        }


def convert_frontend_widget_to_backend(widget: Dict[str, Any]) -> Dict[str, Any]:
    """Convert frontend widget format to backend component format."""
    widget_type = widget.get("type", "bar")
    backend_type_map = {
        "bar": "bar_chart",
        "line": "line_chart",
        "pie": "pie_chart",
        "kpi": "kpi",
        "table": "table"
    }
    
    position = widget.get("position", {})
    
    return {
        "id": widget.get("id", ""),
        "type": backend_type_map.get(widget_type, "bar_chart"),
        "title": widget.get("title", ""),
        "config": {
            "x_axis": widget.get("config", {}).get("xAxis"),
            "y_axis": widget.get("config", {}).get("yAxis"),
            "aggregation": widget.get("config", {}).get("aggregation", "sum"),
            "gradient": widget.get("config", {}).get("gradient")
        },
        "position": {
            "row": position.get("y", 0),
            "col": position.get("x", 0),
            "width": position.get("w", 6),
            "height": position.get("h", 2)
        }
    }


def convert_backend_component_to_frontend(component: Dict[str, Any], dataset_id: str) -> Dict[str, Any]:
    """Convert backend component format to frontend widget format."""
    component_type = component.get("type", "bar_chart")
    frontend_type_map = {
        "bar_chart": "bar",
        "line_chart": "line",
        "pie_chart": "pie",
        "kpi": "kpi",
        "table": "table"
    }
    
    config = component.get("config", {})
    position = component.get("position", {})
    
    widget = {
        "id": component.get("id", ""),
        "type": frontend_type_map.get(component_type, "bar"),
        "title": component.get("title", ""),
        "datasetId": dataset_id,
        "config": {
            "xAxis": config.get("x_axis"),
            "yAxis": config.get("y_axis"),
            "aggregation": config.get("aggregation", "sum"),
            "gradient": config.get("gradient") or get_default_gradient(frontend_type_map.get(component_type, "bar"))
        },
        "position": {
            "x": position.get("col", 0),
            "y": position.get("row", 0),
            "w": position.get("width", 6),
            "h": position.get("height", 2)
        }
    }
    
    return widget


def get_default_gradient(widget_type: str) -> List[str]:
    """Get default gradient colors for widget type."""
    gradients = {
        "bar": ["#00d9ff", "#00a8cc"],
        "line": ["#a855f7", "#ec4899"],
        "pie": ["#10b981", "#059669"],
        "kpi": ["#10b981", "#059669"]
    }
    return gradients.get(widget_type, ["#00d9ff", "#00a8cc"])

