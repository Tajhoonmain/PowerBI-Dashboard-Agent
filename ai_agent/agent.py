"""Main AI agent orchestrator."""
from typing import Dict, Any, List
from ai_agent.intent_parser import IntentParser
from ai_agent.action_generator import ActionGenerator


class DashboardAgent:
    """Main AI agent for dashboard modifications."""
    
    def __init__(self):
        self.intent_parser = IntentParser()
        self.action_generator = ActionGenerator()
        self.conversation_history = []
        self.last_intent = {}  # Store last parsed intent for evaluation
    
    def process_command(
        self,
        user_command: str,
        dashboard_state: Dict[str, Any],
        available_columns: List[Dict[str, Any]],
        dataset_data: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user command and return action to modify dashboard.
        
        Args:
            user_command: User's natural language command
            dashboard_state: Current dashboard state
            available_columns: List of column metadata
            dataset_data: Optional dataset data for analysis (for explain_chart)
        
        Returns: Action result with success, action details, and explanation
        """
        # Parse intent
        intent = self.intent_parser.parse_intent(
            user_command,
            dashboard_state,
            available_columns
        )
        self.last_intent = intent  # Store for evaluation
        
        # Add dataset data to dashboard state for explain_chart and answer_question
        if dataset_data:
            action_type = intent.get("action_type")
            if action_type in ["explain_chart", "answer_question"]:
                # For Q&A, include more data for better analysis
                limit = 500 if action_type == "answer_question" else 100
                dashboard_state["_dataset_data"] = dataset_data[:limit]
        
        # Generate action (pass full column metadata, not just names)
        action = self.action_generator.generate_action(
            intent,
            dashboard_state,
            available_columns
        )
        
        # Store in conversation history
        self.conversation_history.append({
            "user_command": user_command,
            "intent": intent,
            "action": action
        })
        
        return action
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

