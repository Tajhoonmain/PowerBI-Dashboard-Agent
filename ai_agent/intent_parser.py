"""Production-grade intent parser with strict JSON enforcement."""
import json
import re
from typing import Dict, Any, Optional, List
from ai_agent.llm.ollama_client import OllamaClient
from backend.config import settings

try:
    from ai_agent.llm.huggingface_client import HuggingFaceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    HuggingFaceClient = None

try:
    from ai_agent.llm.gemini_client import GeminiClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    GeminiClient = None


class IntentParser:
    """Parse user intents with strict JSON-only output enforcement."""
    
    def __init__(self):
        if settings.llm_provider == "gemini" and GEMINI_AVAILABLE:
            try:
                self.llm = GeminiClient()
            except Exception as e:
                print(f"Warning: Gemini not available ({e}), falling back to Ollama")
                self.llm = OllamaClient()
        elif settings.llm_provider == "ollama":
            self.llm = OllamaClient()
        elif settings.llm_provider == "huggingface" and HF_AVAILABLE:
            self.llm = HuggingFaceClient()
        else:
            print("Warning: Preferred LLM not available, falling back to Ollama")
            self.llm = OllamaClient()
    
    def parse_intent(
        self,
        user_command: str,
        dashboard_state: Dict[str, Any],
        available_columns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Parse user command into structured action.
        
        Returns: Action dictionary with action_type, parameters, etc.
        """
        # Build context (METADATA ONLY - no raw data)
        context = self._build_context(dashboard_state, available_columns)
        
        # Create strict JSON-only prompt
        prompt = self._create_prompt(user_command, context)
        
        # Get system prompt
        system_prompt = self._get_system_prompt()
        
        # Generate response
        try:
            print(f"[INTENT PARSER] User command: {user_command}")
            print(f"[INTENT PARSER] Available columns: {[c.get('name') for c in available_columns]}")
            print(f"[INTENT PARSER] Sending to LLM...")
            
            response = self.llm.generate(prompt, system_prompt)
            print(f"[INTENT PARSER] LLM raw response: {response[:200]}...")  # First 200 chars
            
            # Extract JSON with multiple fallback strategies
            action = self._extract_json_strict(response)
            print(f"[INTENT PARSER] Parsed action: {action}")
            
            # Validate action structure
            action = self._validate_action(action)
            # Store user command for fallback detection
            action["user_command"] = user_command
            print(f"[INTENT PARSER] Validated action: {action}")
            
            return action
        except Exception as e:
            print(f"LLM parsing error: {e}")
            # Fallback to rule-based parsing
            return self._rule_based_parse(user_command, dashboard_state, available_columns)
    
    def _build_context(self, dashboard_state: Dict[str, Any], available_columns: List[Dict[str, Any]]) -> str:
        """
        Build context string with METADATA ONLY.
        NEVER include raw data - only column names, types, stats, sample rows.
        """
        context_parts = []
        
        # Column metadata (type, sample values, stats - NO raw data)
        context_parts.append("AVAILABLE COLUMNS (metadata only):")
        for col in available_columns[:20]:  # Limit to prevent token waste
            col_info = f"  - {col.get('name')} ({col.get('type')})"
            if col.get('sample_values'):
                samples = col.get('sample_values', [])[:3]
                col_info += f" [samples: {', '.join(map(str, samples))}]"
            context_parts.append(col_info)
        
        # Dashboard component metadata (IDs, types, titles - NO data)
        if dashboard_state.get('components'):
            context_parts.append("\nCURRENT DASHBOARD COMPONENTS:")
            for comp in dashboard_state['components']:
                comp_info = f"  - ID: {comp.get('id')}, Type: {comp.get('type')}, Title: {comp.get('title')}"
                if comp.get('config'):
                    config = comp.get('config', {})
                    if 'x_axis' in config:
                        comp_info += f", X-axis: {config.get('x_axis')}"
                    if 'y_axis' in config:
                        comp_info += f", Y-axis: {config.get('y_axis')}"
                context_parts.append(comp_info)
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, user_command: str, context: str) -> str:
        """Create strict JSON-only prompt."""
        return f"""CONTEXT:
{context}

USER COMMAND: "{user_command}"

INSTRUCTIONS:
1. FIRST: Determine the action type based on the command:
   - Questions starting with "what", "which", "how many", "how much", "what's", "what are", "show me the" → use "answer_question"
   - Questions about charts like "what does this chart mean", "explain this chart" → use "explain_chart"
   - Commands to create visualizations → use "add_chart", "generate_dashboard", etc.
2. Extract column names from the user's command
3. Match them to the AVAILABLE COLUMNS in the context above
4. Use EXACT column names from the AVAILABLE COLUMNS list
5. For bar/line charts: x_axis = categorical column, y_axis = numeric column
6. For KPI: y_axis = numeric column (no x_axis)
7. If user says "by [column]", that column is the x_axis
8. If user mentions a metric (revenue, sales, quantity, etc.), that's the y_axis

OUTPUT REQUIREMENTS:
- Output ONLY valid JSON
- No markdown code blocks
- No explanations outside JSON
- No text before or after JSON
- Use the exact format specified in system prompt

RESPOND WITH JSON ONLY:"""
    
    def _get_system_prompt(self) -> str:
        """Get system prompt."""
        try:
            with open("ai_agent/prompts/system_prompt.txt", "r") as f:
                return f.read()
        except:
            return "You are a BI Dashboard Assistant. Output ONLY valid JSON."
    
    def _extract_json_strict(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON with multiple fallback strategies.
        Production-grade parsing.
        """
        # Strategy 1: Try to find JSON object (handles nested braces)
        json_patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Simple nested
            r'\{.*?\}',  # Greedy match
            r'```json\s*(\{.*?\})\s*```',  # Markdown code block
            r'```\s*(\{.*?\})\s*```',  # Code block without json
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                json_str = match if isinstance(match, str) else match.group(1) if hasattr(match, 'group') else match
                try:
                    parsed = json.loads(json_str)
                    if isinstance(parsed, dict) and "action_type" in parsed:
                        return parsed
                except json.JSONDecodeError:
                    continue
        
        # Strategy 2: Try to clean and parse entire response
        cleaned = text.strip()
        # Remove markdown code blocks
        cleaned = re.sub(r'```json\s*', '', cleaned)
        cleaned = re.sub(r'```\s*', '', cleaned)
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # Try to find JSON object boundaries
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = cleaned[start_idx:end_idx + 1]
            try:
                parsed = json.loads(json_str)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Return unknown action
        return {
            "action_type": "unknown",
            "target_component": None,
            "parameters": {},
            "explanation": "Could not parse JSON from response. Please try rephrasing your command."
        }
    
    def _validate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize action structure."""
        # Ensure required fields exist
        if "action_type" not in action:
            action["action_type"] = "unknown"
        
        if "target_component" not in action:
            action["target_component"] = None
        
        if "parameters" not in action:
            action["parameters"] = {}
        
        if "explanation" not in action:
            action["explanation"] = "Processing your request."
        
        # Validate action_type
        valid_actions = [
            "generate_dashboard", "add_chart", "modify_chart", "remove_chart",
            "explain_chart", "answer_question", "filter_data", "transform_data", "update_kpi", "rename_component", "unknown"
        ]
        if action["action_type"] not in valid_actions:
            action["action_type"] = "unknown"
            action["explanation"] = f"Unknown action type. Available: {', '.join(valid_actions)}"
        
        return action
    
    def _rule_based_parse(
        self,
        command: str,
        dashboard_state: Dict[str, Any],
        available_columns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback rule-based parsing when LLM fails."""
        command_lower = command.lower()
        
        # Enhanced pattern matching - catch more visualization requests
        visualization_keywords = ["chart", "graph", "visualization", "visualize", "plot", "show", "display", "create", "add", "make", "generate"]
        chart_type_keywords = {
            "bar": "bar_chart",
            "line": "line_chart",
            "pie": "pie_chart",
            "kpi": "kpi",
            "metric": "kpi",
            "total": "kpi",
            "table": "table"
        }
        
        # Check if it's a visualization request
        is_visualization = any(word in command_lower for word in visualization_keywords)
        
        if is_visualization:
            # Determine chart type
            chart_type = "bar_chart"  # default
            for keyword, ctype in chart_type_keywords.items():
                if keyword in command_lower:
                    chart_type = ctype
                    break
            
            # Try to extract columns from command
            # Look for common patterns like "X by Y" or "X over Y"
            x_axis = None
            y_axis = None
            
            # Get available columns
            numeric_cols = [c.get('name') for c in available_columns if c.get('type') == 'numeric']
            string_cols = [c.get('name') for c in available_columns if c.get('type') == 'string']
            date_cols = [c.get('name') for c in available_columns if c.get('type') == 'date']
            
            # Pattern 1: "X by Y" or "X per Y"
            by_match = re.search(r'(\w+)\s+by\s+(\w+)', command_lower)
            if by_match:
                metric = by_match.group(1)
                category = by_match.group(2)
                # Find matching columns
                for col in available_columns:
                    col_name_lower = col.get('name', '').lower()
                    if metric in col_name_lower or col_name_lower in metric:
                        if col.get('type') == 'numeric':
                            y_axis = col.get('name')
                    if category in col_name_lower or col_name_lower in category:
                        if col.get('type') in ['string', 'date']:
                            x_axis = col.get('name')
            
            # Pattern 2: Look for column names directly in command
            if not x_axis or not y_axis:
                for col in available_columns:
                    col_name = col.get('name', '').lower()
                    col_name_clean = col_name.replace('_', ' ').replace('-', ' ')
                    # Check if column name appears in command
                    if col_name in command_lower or col_name_clean in command_lower:
                        if col.get('type') == 'numeric' and not y_axis:
                            y_axis = col.get('name')
                        elif col.get('type') in ['string', 'date'] and not x_axis:
                            x_axis = col.get('name')
            
            # Pattern 3: Common metric keywords
            metric_keywords = ['revenue', 'sales', 'quantity', 'amount', 'price', 'cost', 'profit', 'total', 'sum', 'count']
            for keyword in metric_keywords:
                if keyword in command_lower and not y_axis:
                    for col in available_columns:
                        if keyword in col.get('name', '').lower() and col.get('type') == 'numeric':
                            y_axis = col.get('name')
                            break
            
            # Pattern 4: Common category keywords
            category_keywords = ['category', 'region', 'product', 'date', 'time', 'month', 'year', 'day']
            for keyword in category_keywords:
                if keyword in command_lower and not x_axis:
                    for col in available_columns:
                        if keyword in col.get('name', '').lower() and col.get('type') in ['string', 'date']:
                            x_axis = col.get('name')
                            break
            
            # Defaults if still not found
            if not x_axis:
                if date_cols:
                    x_axis = date_cols[0]
                elif string_cols:
                    x_axis = string_cols[0]
            if not y_axis and numeric_cols:
                y_axis = numeric_cols[0]
            
            params = {"chart_type": chart_type}
            if x_axis:
                params["x_axis"] = x_axis
            if y_axis:
                params["y_axis"] = y_axis
            
            return {
                "action_type": "add_chart",
                "target_component": None,
                "parameters": params,
                "explanation": f"Adding {chart_type} to dashboard"
            }
        
        if any(word in command_lower for word in ["remove", "delete", "drop"]):
            return {
                "action_type": "remove_chart",
                "target_component": None,
                "parameters": {},
                "explanation": "Removing component from dashboard"
            }
        
        if "filter" in command_lower or "show only" in command_lower or "top" in command_lower:
            return {
                "action_type": "filter_data",
                "target_component": None,
                "parameters": {},
                "explanation": "Applying filter to data"
            }
        
        if any(word in command_lower for word in ["change", "modify", "update", "switch"]):
            return {
                "action_type": "modify_chart",
                "target_component": None,
                "parameters": {},
                "explanation": "Modifying chart as requested"
            }
        
        if "rename" in command_lower:
            return {
                "action_type": "rename_component",
                "target_component": None,
                "parameters": {},
                "explanation": "Renaming component"
            }
        
        return {
            "action_type": "unknown",
            "target_component": None,
            "parameters": {},
            "explanation": "I didn't understand that command. Please try rephrasing or be more specific."
        }
