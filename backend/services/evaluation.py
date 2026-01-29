"""Agent evaluation and benchmarking service."""
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class EvaluationMetric(Enum):
    """Evaluation metrics."""
    TASK_SUCCESS_RATE = "task_success_rate"
    ACTION_CORRECTNESS = "action_correctness"
    LATENCY = "latency"
    COST_EFFICIENCY = "cost_efficiency"
    REASONING_LENGTH = "reasoning_length"
    TOOL_USAGE_CORRECTNESS = "tool_usage_correctness"


@dataclass
class EvaluationResult:
    """Single evaluation result."""
    task_id: str
    timestamp: datetime
    user_command: str
    intent_parsed: Dict[str, Any]
    action_generated: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    
    # Metrics
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    response_tokens: int = 0
    estimated_cost: float = 0.0
    action_correctness_score: float = 0.0
    tool_usage_correct: bool = True
    
    # Metadata
    llm_provider: str = ""
    action_type: str = ""
    execution_time_ms: float = 0.0


class AgentEvaluator:
    """Evaluates agent performance across multiple metrics."""
    
    def __init__(self):
        self.evaluation_history: List[EvaluationResult] = []
        self.current_task_id: Optional[str] = None
        self.start_time: Optional[float] = None
        self.prompt_size: int = 0
        self.response_size: int = 0
    
    def start_evaluation(self, task_id: str, user_command: str):
        """Start tracking an evaluation."""
        self.current_task_id = task_id
        self.start_time = time.time()
        self.prompt_size = 0
        self.response_size = 0
    
    def track_prompt_size(self, prompt: str):
        """Track prompt size (for token estimation)."""
        self.prompt_size = len(prompt.split())  # Rough token estimate
    
    def track_response_size(self, response: str):
        """Track response size (for token estimation)."""
        self.response_size = len(response.split())  # Rough token estimate
    
    def record_intent(self, intent: Dict[str, Any]):
        """Record parsed intent."""
        self.current_intent = intent
    
    def record_action(self, action: Dict[str, Any]):
        """Record generated action."""
        self.current_action = action
    
    def complete_evaluation(
        self,
        user_command: str,
        intent: Dict[str, Any],
        action: Dict[str, Any],
        success: bool,
        error_message: Optional[str] = None,
        llm_provider: str = "gemini"
    ) -> EvaluationResult:
        """Complete evaluation and calculate metrics."""
        if not self.start_time:
            self.start_time = time.time()
        
        end_time = time.time()
        latency_ms = (end_time - self.start_time) * 1000
        
        # Calculate metrics
        action_correctness = self._calculate_action_correctness(intent, action)
        tool_usage_correct = self._check_tool_usage_correctness(intent, action)
        estimated_cost = self._estimate_cost(llm_provider, self.prompt_size, self.response_size)
        
        result = EvaluationResult(
            task_id=self.current_task_id or f"task_{int(time.time())}",
            timestamp=datetime.now(),
            user_command=user_command,
            intent_parsed=intent,
            action_generated=action,
            success=success,
            error_message=error_message,
            latency_ms=latency_ms,
            prompt_tokens=self.prompt_size,
            response_tokens=self.response_size,
            estimated_cost=estimated_cost,
            action_correctness_score=action_correctness,
            tool_usage_correct=tool_usage_correct,
            llm_provider=llm_provider,
            action_type=intent.get("action_type", "unknown"),
            execution_time_ms=latency_ms
        )
        
        self.evaluation_history.append(result)
        return result
    
    def _calculate_action_correctness(self, intent: Dict[str, Any], action: Dict[str, Any]) -> float:
        """Calculate how well the action matches the intent (0.0 to 1.0)."""
        score = 0.0
        
        # Check if action type matches intent
        intent_action_type = intent.get("action_type", "")
        action_action_type = action.get("action", "") or action.get("action_type", "")
        
        if intent_action_type and action_action_type:
            if intent_action_type == action_action_type:
                score += 0.4
            elif intent_action_type in ["unknown"] and action_action_type != "unknown":
                score += 0.2  # Partial credit for recovering from unknown
        
        # Check if action succeeded
        if action.get("success", False):
            score += 0.3
        
        # Check parameter matching
        intent_params = intent.get("parameters", {})
        action_params = action.get("parameters", {}) or {}
        
        if intent_params and action_params:
            matching_params = sum(
                1 for k, v in intent_params.items()
                if k in action_params and action_params[k] == v
            )
            if len(intent_params) > 0:
                score += 0.3 * (matching_params / len(intent_params))
        
        return min(score, 1.0)
    
    def _check_tool_usage_correctness(self, intent: Dict[str, Any], action: Dict[str, Any]) -> bool:
        """Check if the correct tool/action was used."""
        intent_action_type = intent.get("action_type", "")
        action_action_type = action.get("action", "") or action.get("action_type", "")
        
        # Valid action types
        valid_actions = [
            "generate_dashboard", "add_chart", "modify_chart", "remove_chart",
            "explain_chart", "answer_question", "filter_data", "transform_data",
            "update_kpi", "rename_component"
        ]
        
        # Check if action type is valid
        if action_action_type not in valid_actions and action_action_type != "unknown":
            return False
        
        # Check if action type matches intent (or is a reasonable alternative)
        if intent_action_type == action_action_type:
            return True
        
        # Allow some flexibility (e.g., add_chart vs generate_dashboard)
        compatible_actions = {
            "add_chart": ["generate_dashboard"],
            "generate_dashboard": ["add_chart"]
        }
        
        if intent_action_type in compatible_actions:
            if action_action_type in compatible_actions[intent_action_type]:
                return True
        
        return False
    
    def _estimate_cost(self, llm_provider: str, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate API cost based on provider and token usage."""
        # Pricing per 1M tokens (as of 2024)
        pricing = {
            "gemini": {
                "gemini-2.5-flash": {"input": 0.075, "output": 0.30},  # $0.075/$0.30 per 1M tokens
                "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
                "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
            },
            "ollama": {"input": 0.0, "output": 0.0},  # Free (local)
            "huggingface": {"input": 0.0, "output": 0.0}  # Free (local)
        }
        
        if llm_provider not in pricing:
            return 0.0
        
        # Use default model pricing for provider
        model_pricing = pricing[llm_provider]
        if isinstance(model_pricing, dict) and "input" in model_pricing:
            input_cost = (prompt_tokens / 1_000_000) * model_pricing["input"]
            output_cost = (response_tokens / 1_000_000) * model_pricing["output"]
            return input_cost + output_cost
        
        return 0.0
    
    def get_task_success_rate(self) -> float:
        """Calculate overall task success rate."""
        if not self.evaluation_history:
            return 0.0
        
        successful = sum(1 for r in self.evaluation_history if r.success)
        return successful / len(self.evaluation_history)
    
    def get_average_latency(self) -> float:
        """Calculate average latency in milliseconds."""
        if not self.evaluation_history:
            return 0.0
        
        total_latency = sum(r.latency_ms for r in self.evaluation_history)
        return total_latency / len(self.evaluation_history)
    
    def get_average_action_correctness(self) -> float:
        """Calculate average action correctness score."""
        if not self.evaluation_history:
            return 0.0
        
        total_score = sum(r.action_correctness_score for r in self.evaluation_history)
        return total_score / len(self.evaluation_history)
    
    def get_total_cost(self) -> float:
        """Calculate total estimated cost."""
        return sum(r.estimated_cost for r in self.evaluation_history)
    
    def get_average_reasoning_length(self) -> Dict[str, float]:
        """Calculate average reasoning length (prompt + response tokens)."""
        if not self.evaluation_history:
            return {"prompt": 0.0, "response": 0.0, "total": 0.0}
        
        avg_prompt = sum(r.prompt_tokens for r in self.evaluation_history) / len(self.evaluation_history)
        avg_response = sum(r.response_tokens for r in self.evaluation_history) / len(self.evaluation_history)
        
        return {
            "prompt": avg_prompt,
            "response": avg_response,
            "total": avg_prompt + avg_response
        }
    
    def get_tool_usage_accuracy(self) -> float:
        """Calculate tool usage correctness rate."""
        if not self.evaluation_history:
            return 0.0
        
        correct = sum(1 for r in self.evaluation_history if r.tool_usage_correct)
        return correct / len(self.evaluation_history)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive evaluation summary."""
        return {
            "total_tasks": len(self.evaluation_history),
            "task_success_rate": self.get_task_success_rate(),
            "average_latency_ms": self.get_average_latency(),
            "average_action_correctness": self.get_average_action_correctness(),
            "total_estimated_cost": self.get_total_cost(),
            "average_reasoning_length": self.get_average_reasoning_length(),
            "tool_usage_accuracy": self.get_tool_usage_accuracy(),
            "metrics_by_action_type": self._get_metrics_by_action_type(),
            "recent_results": [
                asdict(r) for r in self.evaluation_history[-10:]
            ]
        }
    
    def _get_metrics_by_action_type(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics grouped by action type."""
        by_type = {}
        
        for result in self.evaluation_history:
            action_type = result.action_type or "unknown"
            if action_type not in by_type:
                by_type[action_type] = {
                    "count": 0,
                    "success_count": 0,
                    "total_latency": 0.0,
                    "total_cost": 0.0
                }
            
            by_type[action_type]["count"] += 1
            if result.success:
                by_type[action_type]["success_count"] += 1
            by_type[action_type]["total_latency"] += result.latency_ms
            by_type[action_type]["total_cost"] += result.estimated_cost
        
        # Calculate averages
        for action_type, metrics in by_type.items():
            count = metrics["count"]
            metrics["success_rate"] = metrics["success_count"] / count if count > 0 else 0.0
            metrics["avg_latency_ms"] = metrics["total_latency"] / count if count > 0 else 0.0
            metrics["avg_cost"] = metrics["total_cost"] / count if count > 0 else 0.0
        
        return by_type
    
    def export_results(self, filepath: str):
        """Export evaluation results to JSON file."""
        data = {
            "summary": self.get_summary(),
            "all_results": [asdict(r) for r in self.evaluation_history]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def clear_history(self):
        """Clear evaluation history."""
        self.evaluation_history = []


# Global evaluator instance
evaluator = AgentEvaluator()

