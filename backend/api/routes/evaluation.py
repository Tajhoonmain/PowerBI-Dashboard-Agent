"""Evaluation API routes."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from backend.database.connection import get_db
from backend.models.evaluation import EvaluationRecord
from backend.services.evaluation import evaluator, EvaluationResult
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/evaluation", tags=["evaluation"])


class EvaluationRequest(BaseModel):
    """Request to record an evaluation."""
    user_command: str
    intent: Dict[str, Any]
    action: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    llm_provider: str = "gemini"
    latency_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    response_tokens: Optional[int] = None


class EvaluationSummaryResponse(BaseModel):
    """Evaluation summary response."""
    total_tasks: int
    task_success_rate: float
    average_latency_ms: float
    average_action_correctness: float
    total_estimated_cost: float
    average_reasoning_length: Dict[str, float]
    tool_usage_accuracy: float
    metrics_by_action_type: Dict[str, Dict[str, Any]]


@router.post("/record", response_model=Dict[str, Any])
async def record_evaluation(
    request: EvaluationRequest,
    db: Session = Depends(get_db)
):
    """Record a single evaluation result."""
    try:
        # Use evaluator to calculate metrics
        evaluator.start_evaluation(
            task_id=str(uuid.uuid4()),
            user_command=request.user_command
        )
        
        if request.prompt_tokens:
            evaluator.prompt_size = request.prompt_tokens
        if request.response_tokens:
            evaluator.response_size = request.response_tokens
        
        result = evaluator.complete_evaluation(
            user_command=request.user_command,
            intent=request.intent,
            action=request.action,
            success=request.success,
            error_message=request.error_message,
            llm_provider=request.llm_provider
        )
        
        # Override latency if provided
        if request.latency_ms:
            result.latency_ms = request.latency_ms
            result.execution_time_ms = request.latency_ms
        
        # Save to database
        record = EvaluationRecord(
            id=str(uuid.uuid4()),
            task_id=result.task_id,
            timestamp=result.timestamp,
            user_command=result.user_command,
            action_type=result.action_type,
            success=result.success,
            error_message=result.error_message,
            latency_ms=result.latency_ms,
            prompt_tokens=result.prompt_tokens,
            response_tokens=result.response_tokens,
            estimated_cost=result.estimated_cost,
            action_correctness_score=result.action_correctness_score,
            tool_usage_correct=result.tool_usage_correct,
            llm_provider=result.llm_provider,
            execution_time_ms=result.execution_time_ms,
            intent_parsed=result.intent_parsed,
            action_generated=result.action_generated
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return {
            "success": True,
            "task_id": result.task_id,
            "metrics": {
                "latency_ms": result.latency_ms,
                "action_correctness": result.action_correctness_score,
                "estimated_cost": result.estimated_cost,
                "tool_usage_correct": result.tool_usage_correct
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error recording evaluation: {str(e)}")


@router.get("/summary", response_model=EvaluationSummaryResponse)
async def get_evaluation_summary(db: Session = Depends(get_db)):
    """Get comprehensive evaluation summary."""
    try:
        summary = evaluator.get_summary()
        
        # Also get from database for historical data
        total_records = db.query(EvaluationRecord).count()
        if total_records > 0:
            # Update summary with database records if available
            successful = db.query(EvaluationRecord).filter(EvaluationRecord.success == True).count()
            summary["total_tasks"] = total_records
            summary["task_success_rate"] = successful / total_records if total_records > 0 else 0.0
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/results", response_model=List[Dict[str, Any]])
async def get_evaluation_results(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get evaluation results with pagination."""
    try:
        records = db.query(EvaluationRecord)\
            .order_by(EvaluationRecord.timestamp.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return [record.to_dict() for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting results: {str(e)}")


@router.get("/metrics/{metric_name}", response_model=Dict[str, Any])
async def get_specific_metric(metric_name: str):
    """Get a specific metric."""
    metric_map = {
        "task_success_rate": lambda: {"value": evaluator.get_task_success_rate(), "unit": "percentage"},
        "latency": lambda: {"value": evaluator.get_average_latency(), "unit": "milliseconds"},
        "action_correctness": lambda: {"value": evaluator.get_average_action_correctness(), "unit": "score"},
        "cost": lambda: {"value": evaluator.get_total_cost(), "unit": "USD"},
        "reasoning_length": lambda: evaluator.get_average_reasoning_length(),
        "tool_usage": lambda: {"value": evaluator.get_tool_usage_accuracy(), "unit": "percentage"}
    }
    
    if metric_name not in metric_map:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_name}' not found")
    
    try:
        result = metric_map[metric_name]()
        return {
            "metric": metric_name,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metric: {str(e)}")


@router.delete("/clear")
async def clear_evaluation_history(db: Session = Depends(get_db)):
    """Clear all evaluation history."""
    try:
        db.query(EvaluationRecord).delete()
        db.commit()
        evaluator.clear_history()
        
        return {"success": True, "message": "Evaluation history cleared"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")


@router.post("/export")
async def export_evaluation_results(filepath: Optional[str] = None):
    """Export evaluation results to JSON file."""
    try:
        if not filepath:
            filepath = f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        evaluator.export_results(filepath)
        
        return {
            "success": True,
            "filepath": filepath,
            "message": f"Results exported to {filepath}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting results: {str(e)}")

