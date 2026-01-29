"""Production-grade action generator with intelligent chart generation."""
from typing import Dict, Any, List, Optional
import uuid
import re


class ActionGenerator:
    """Generate dashboard modification actions from parsed intents."""
    
    @staticmethod
    def generate_action(
        intent: Dict[str, Any],
        dashboard: Dict[str, Any],
        available_columns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a concrete action from intent.
        
        Returns: Action with specific parameters filled in
        """
        action_type = intent.get("action_type")
        parameters = intent.get("parameters", {})
        
        # Fallback: If action_type is "unknown" but looks like a question, treat it as answer_question
        if action_type == "unknown":
            explanation = intent.get("explanation", "").lower()
            user_command_lower = str(intent.get("user_command", "")).lower() if "user_command" in intent else ""
            question_indicators = ["what", "which", "how many", "how much", "what's", "what are", "show me the", "tell me"]
            
            if any(indicator in explanation or indicator in user_command_lower for indicator in question_indicators):
                # Force it to be answer_question
                action_type = "answer_question"
                parameters = {"question": intent.get("explanation", "") or user_command_lower}
                print(f"[ACTION_GENERATOR] Detected question, converting unknown to answer_question")
        
        # Categorize columns by type
        column_info = ActionGenerator._categorize_columns(available_columns)
        
        if action_type == "generate_dashboard":
            return ActionGenerator._generate_full_dashboard(
                dashboard, parameters, column_info, intent, available_columns
            )
        elif action_type == "add_chart":
            return ActionGenerator._generate_add_chart(
                dashboard, parameters, column_info, intent
            )
        elif action_type == "explain_chart":
            return ActionGenerator._generate_explain_chart(
                dashboard, parameters, intent, available_columns
            )
        elif action_type == "answer_question":
            return ActionGenerator._generate_answer_question(
                dashboard, parameters, intent, available_columns
            )
        elif action_type == "modify_chart":
            return ActionGenerator._generate_modify_chart(dashboard, parameters, intent)
        elif action_type == "remove_chart":
            return ActionGenerator._generate_remove_chart(dashboard, parameters, intent)
        elif action_type == "filter_data":
            return ActionGenerator._generate_filter(dashboard, parameters, column_info, intent)
        elif action_type == "transform_data":
            return ActionGenerator._generate_transform(dashboard, parameters, column_info, intent)
        elif action_type == "update_kpi":
            return ActionGenerator._generate_update_kpi(dashboard, parameters, intent)
        elif action_type == "rename_component":
            return ActionGenerator._generate_rename_component(dashboard, parameters, intent)
        elif action_type == "unknown":
            # Provide helpful suggestions for unknown commands
            explanation = intent.get("explanation", "I didn't understand that command.")
            suggestions = [
                "Try: 'Create a bar chart showing [metric] by [category]'",
                "Try: 'Show me [metric]'",
                "Try: 'Display total [metric]'",
                "Try: 'Add a line chart for [metric] over time'",
                "Try: 'Show KPIs for [metric]'",
                "Try: 'What are the top 5 [items] by [metric]?'",
                "Try: 'What's the average [metric]?'",
                "Try: 'Which [category] has the highest [metric]?'"
            ]
            return {
                "success": False,
                "error": "Unknown action type",
                "explanation": f"{explanation}\n\nAvailable commands:\n" + "\n".join(f"- {s}" for s in suggestions),
                "suggestions": suggestions
            }
        else:
            return {
                "success": False,
                "error": f"Unknown action type: {action_type}",
                "explanation": intent.get("explanation", "Unknown action. Try commands like 'Create a bar chart' or 'Show me revenue'.")
            }
    
    @staticmethod
    def _categorize_columns(columns: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Categorize columns by type."""
        result = {
            "numeric": [],
            "string": [],
            "date": [],
            "boolean": []
        }
        
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "string")
            if col_type in result:
                result[col_type].append(col_name)
        
        return result
    
    @staticmethod
    def _generate_add_chart(
        dashboard: Dict[str, Any],
        parameters: Dict[str, Any],
        column_info: Dict[str, List[str]],
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate add chart action with intelligent column selection."""
        chart_type = parameters.get("chart_type", "bar_chart")
        
        # Extract axes from parameters or infer intelligently
        x_axis = parameters.get("x_axis")
        y_axis = parameters.get("y_axis")
        
        print(f"[ACTION GENERATOR] Chart type: {chart_type}")
        print(f"[ACTION GENERATOR] Parameters: {parameters}")
        print(f"[ACTION GENERATOR] Column info: {column_info}")
        print(f"[ACTION GENERATOR] Extracted x_axis: {x_axis}, y_axis: {y_axis}")
        
        # Intelligent defaults if not specified
        if not x_axis and column_info["string"]:
            x_axis = column_info["string"][0]
            print(f"[ACTION GENERATOR] Using default x_axis: {x_axis}")
        if not y_axis and column_info["numeric"]:
            y_axis = column_info["numeric"][0]
            print(f"[ACTION GENERATOR] Using default y_axis: {y_axis}")
        
        # Validate we have required columns
        if chart_type in ["bar_chart", "line_chart"]:
            if not x_axis or not y_axis:
                return {
                    "success": False,
                    "error": "Need both X-axis (categorical) and Y-axis (numeric) columns",
                    "explanation": "Cannot create chart: missing required columns"
                }
        elif chart_type == "pie_chart":
            if not x_axis or not y_axis:
                # Pie chart needs category and value
                if column_info["string"] and column_info["numeric"]:
                    x_axis = column_info["string"][0]
                    y_axis = column_info["numeric"][0]
                else:
                    return {
                        "success": False,
                        "error": "Pie chart requires categorical and numeric columns",
                        "explanation": "Cannot create pie chart: insufficient columns"
                    }
        
        # Determine position
        existing_components = dashboard.get("components", [])
        row = len(existing_components)
        col = 0
        
        # Generate title
        title = parameters.get("title")
        if not title:
            if x_axis and y_axis:
                title = f"{y_axis.replace('_', ' ').title()} by {x_axis.replace('_', ' ').title()}"
            else:
                title = f"New {chart_type.replace('_', ' ').title()}"
        
        new_component = {
            "id": str(uuid.uuid4()),
            "type": chart_type,
            "title": title,
            "config": {
                "x_axis": x_axis,
                "y_axis": y_axis,
                "aggregation": parameters.get("aggregation", "sum"),
                "data": []  # Will be populated by dashboard generator
            },
            "position": {
                "row": row,
                "col": col,
                "width": 2,
                "height": 2
            }
        }
        
        return {
            "success": True,
            "action": "add_component",
            "component": new_component,
            "explanation": intent.get("explanation", f"Added {chart_type} to dashboard")
        }
    
    @staticmethod
    def _generate_modify_chart(
        dashboard: Dict[str, Any],
        parameters: Dict[str, Any],
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate modify chart action."""
        target_id = intent.get("target_component")
        
        # Find target component
        if not target_id:
            components = dashboard.get("components", [])
            # Try to find chart components first
            chart_components = [c for c in components if c.get("type") in ["bar_chart", "line_chart", "pie_chart"]]
            if chart_components:
                target_id = chart_components[0]["id"]
            elif components:
                target_id = components[0]["id"]
            else:
                return {
                    "success": False,
                    "error": "No component to modify",
                    "explanation": "No components found in dashboard"
                }
        
        # Build updates
        updates = {}
        
        # Chart type change
        if "chart_type" in parameters or "type" in parameters:
            new_type = parameters.get("chart_type") or parameters.get("type")
            if new_type in ["bar_chart", "line_chart", "pie_chart", "scatter_chart"]:
                updates["type"] = new_type
        
        # Title change
        if "title" in parameters:
            updates["title"] = parameters["title"]
        
        # Axis changes
        if "x_axis" in parameters or "y_axis" in parameters:
            if "config" not in updates:
                updates["config"] = {}
            if "x_axis" in parameters:
                updates["config"]["x_axis"] = parameters["x_axis"]
            if "y_axis" in parameters:
                updates["config"]["y_axis"] = parameters["y_axis"]
        
        if not updates:
            return {
                "success": False,
                "error": "No valid updates specified",
                "explanation": "Please specify what to modify (type, title, axes, etc.)"
            }
        
        return {
            "success": True,
            "action": "update_component",
            "component_id": target_id,
            "updates": updates,
            "explanation": intent.get("explanation", "Modified chart")
        }
    
    @staticmethod
    def _generate_remove_chart(
        dashboard: Dict[str, Any],
        parameters: Dict[str, Any],
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate remove chart action."""
        target_id = intent.get("target_component")
        
        if not target_id:
            components = dashboard.get("components", [])
            if components:
                # Remove last component by default
                target_id = components[-1]["id"]
            else:
                return {
                    "success": False,
                    "error": "No component to remove",
                    "explanation": "No components found in dashboard"
                }
        
        return {
            "success": True,
            "action": "remove_component",
            "component_id": target_id,
            "explanation": intent.get("explanation", "Removed component")
        }
    
    @staticmethod
    def _generate_filter(
        dashboard: Dict[str, Any],
        parameters: Dict[str, Any],
        column_info: Dict[str, List[str]],
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate filter action with intelligent parsing."""
        # Extract filter parameters
        filter_params = {
            "column": parameters.get("column"),
            "operator": parameters.get("operator", "eq"),
            "value": parameters.get("value"),
            "limit": parameters.get("limit"),
            "sort_by": parameters.get("sort_by"),
            "order": parameters.get("order", "desc")
        }
        
        # If "top N" command, set limit
        explanation = intent.get("explanation", "")
        top_match = re.search(r'top\s+(\d+)', explanation.lower())
        if top_match:
            filter_params["limit"] = int(top_match.group(1))
        
        return {
            "success": True,
            "action": "apply_filter",
            "filter": filter_params,
            "explanation": intent.get("explanation", "Applied filter to data")
        }
    
    @staticmethod
    def _generate_transform(
        dashboard: Dict[str, Any],
        parameters: Dict[str, Any],
        column_info: Dict[str, List[str]],
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate transform action."""
        return {
            "success": True,
            "action": "apply_transformation",
            "transformation": parameters,
            "explanation": intent.get("explanation", "Applied transformation to data")
        }
    
    @staticmethod
    def _generate_update_kpi(
        dashboard: Dict[str, Any],
        parameters: Dict[str, Any],
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate update KPI action."""
        target_id = intent.get("target_component")
        
        if not target_id:
            # Find first KPI component
            components = dashboard.get("components", [])
            kpi_components = [c for c in components if c.get("type") == "kpi"]
            if kpi_components:
                target_id = kpi_components[0]["id"]
            else:
                return {
                    "success": False,
                    "error": "No KPI component found",
                    "explanation": "No KPI cards in dashboard to update"
                }
        
        updates = {}
        if "value" in parameters:
            updates["config"] = {"value": parameters["value"]}
        if "title" in parameters:
            updates["title"] = parameters["title"]
        
        return {
            "success": True,
            "action": "update_component",
            "component_id": target_id,
            "updates": updates,
            "explanation": intent.get("explanation", "Updated KPI")
        }
    
    @staticmethod
    def _generate_rename_component(
        dashboard: Dict[str, Any],
        parameters: Dict[str, Any],
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate rename component action."""
        target_id = intent.get("target_component")
        new_title = parameters.get("title") or parameters.get("new_title")
        
        if not new_title:
            return {
                "success": False,
                "error": "No new title specified",
                "explanation": "Please specify the new title for the component"
            }
        
        if not target_id:
            components = dashboard.get("components", [])
            if components:
                target_id = components[0]["id"]
            else:
                return {
                    "success": False,
                    "error": "No component to rename",
                    "explanation": "No components found in dashboard"
                }
        
        return {
            "success": True,
            "action": "update_component",
            "component_id": target_id,
            "updates": {"title": new_title},
            "explanation": intent.get("explanation", f"Renamed component to '{new_title}'")
        }
    
    @staticmethod
    def _generate_full_dashboard(
        dashboard: Dict[str, Any],
        parameters: Dict[str, Any],
        column_info: Dict[str, List[str]],
        intent: Dict[str, Any],
        available_columns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a complete dashboard with multiple widgets."""
        widgets_spec = parameters.get("widgets", [])
        components = []
        
        # If LLM provided widget specs, use them; otherwise generate intelligently
        if widgets_spec:
            existing_components = dashboard.get("components", [])
            row = len(existing_components)
            
            for i, widget_spec in enumerate(widgets_spec):
                chart_type = widget_spec.get("chart_type", "bar_chart")
                x_axis = widget_spec.get("x_axis")
                y_axis = widget_spec.get("y_axis")
                title = widget_spec.get("title", "")
                
                # Validate columns
                if chart_type in ["bar_chart", "line_chart"]:
                    if not x_axis or not y_axis:
                        # Use defaults if not specified
                        if not x_axis and column_info["string"]:
                            x_axis = column_info["string"][0]
                        if not y_axis and column_info["numeric"]:
                            y_axis = column_info["numeric"][0]
                
                if chart_type == "kpi":
                    if not y_axis and column_info["numeric"]:
                        y_axis = column_info["numeric"][0]
                
                # Map chart_type to backend type
                type_map = {
                    "bar_chart": "bar_chart",
                    "line_chart": "line_chart",
                    "pie_chart": "pie_chart",
                    "kpi": "kpi",
                    "table": "table"
                }
                backend_type = type_map.get(chart_type, "bar_chart")
                
                # Generate title if not provided
                if not title:
                    if x_axis and y_axis:
                        title = f"{y_axis.replace('_', ' ').title()} by {x_axis.replace('_', ' ').title()}"
                    elif y_axis:
                        title = f"Total {y_axis.replace('_', ' ').title()}"
                    else:
                        title = f"{chart_type.replace('_', ' ').title()}"
                
                # Calculate position
                col = (i % 3) * 4  # 3 widgets per row
                current_row = row + (i // 3)
                
                component = {
                    "id": str(uuid.uuid4()),
                    "type": backend_type,
                    "title": title,
                    "config": {
                        "x_axis": x_axis,
                        "y_axis": y_axis,
                        "aggregation": "sum"
                    },
                    "position": {
                        "row": current_row,
                        "col": col,
                        "width": 4,
                        "height": 2 if chart_type != "kpi" else 1
                    }
                }
                components.append(component)
        else:
            # Intelligent dashboard generation
            existing_components = dashboard.get("components", [])
            row = len(existing_components)
            col = 0
            
            # Generate KPIs (2-3 for top numeric columns)
            for i, numeric_col in enumerate(column_info["numeric"][:3]):
                components.append({
                    "id": str(uuid.uuid4()),
                    "type": "kpi",
                    "title": f"Total {numeric_col.replace('_', ' ').title()}",
                    "config": {
                        "x_axis": None,
                        "y_axis": numeric_col,
                        "aggregation": "sum"
                    },
                    "position": {
                        "row": row,
                        "col": col,
                        "width": 4,
                        "height": 1
                    }
                })
                col += 4
                if col >= 12:
                    col = 0
                    row += 1
            
            # Generate bar charts
            if column_info["string"] and column_info["numeric"]:
                for i, string_col in enumerate(column_info["string"][:2]):
                    if col + 6 > 12:
                        col = 0
                        row += 2
                    components.append({
                        "id": str(uuid.uuid4()),
                        "type": "bar_chart",
                        "title": f"{column_info['numeric'][0].replace('_', ' ').title()} by {string_col.replace('_', ' ').title()}",
                        "config": {
                            "x_axis": string_col,
                            "y_axis": column_info["numeric"][0],
                            "aggregation": "sum"
                        },
                        "position": {
                            "row": row,
                            "col": col,
                            "width": 6,
                            "height": 2
                        }
                    })
                    col += 6
            
            # Generate line chart if date column exists
            if column_info["date"] and column_info["numeric"]:
                if col + 6 > 12:
                    col = 0
                    row += 2
                components.append({
                    "id": str(uuid.uuid4()),
                    "type": "line_chart",
                    "title": f"{column_info['numeric'][0].replace('_', ' ').title()} Trend",
                    "config": {
                        "x_axis": column_info["date"][0],
                        "y_axis": column_info["numeric"][0],
                        "aggregation": "sum"
                    },
                    "position": {
                        "row": row,
                        "col": col,
                        "width": 6,
                        "height": 2
                    }
                })
        
        return {
            "success": True,
            "action": "add_multiple_components",
            "components": components,
            "explanation": intent.get("explanation", f"Generated comprehensive dashboard with {len(components)} widgets")
        }
    
    @staticmethod
    def _generate_explain_chart(
        dashboard: Dict[str, Any],
        parameters: Dict[str, Any],
        intent: Dict[str, Any],
        available_columns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate explanation for a chart with insights and decision-making implications."""
        from ai_agent.llm.gemini_client import GeminiClient
        from backend.config import settings
        import json
        
        chart_id = parameters.get("chart_id") or intent.get("target_component")
        question = parameters.get("question", "")
        
        # Find the chart component if ID provided
        chart_info = None
        components = dashboard.get("components", [])
        if chart_id:
            for comp in components:
                if comp.get("id") == chart_id:
                    chart_info = comp
                    break
        elif components:
            # Use first chart if no ID specified
            chart_info = components[0]
        
        # Get dataset data if available
        dataset_data = dashboard.get("_dataset_data", [])
        
        # Build context for LLM analysis
        analysis_context = f"CHART INFORMATION:\n"
        if chart_info:
            analysis_context += f"Type: {chart_info.get('type', 'unknown')}\n"
            analysis_context += f"Title: {chart_info.get('title', 'Untitled')}\n"
            config = chart_info.get('config', {})
            if config.get('x_axis'):
                analysis_context += f"X-axis: {config.get('x_axis')}\n"
            if config.get('y_axis'):
                analysis_context += f"Y-axis: {config.get('y_axis')}\n"
        
        analysis_context += f"\nAVAILABLE DATA COLUMNS:\n"
        for col in available_columns:
            analysis_context += f"- {col.get('name')} ({col.get('type')})\n"
        
        # Add sample data summary if available
        if dataset_data:
            analysis_context += f"\nSAMPLE DATA (first 10 rows):\n"
            for i, row in enumerate(dataset_data[:10]):
                analysis_context += f"Row {i+1}: {json.dumps(row, default=str)}\n"
        
        # Use LLM to generate detailed explanation
        try:
            llm = GeminiClient()
            analysis_prompt = f"""{analysis_context}

USER QUESTION: "{question}"

Provide a detailed analysis of this chart including:
1. What the chart shows (data summary)
2. Key insights and patterns
3. Trends and anomalies
4. Business implications and decision-making recommendations
5. Actionable next steps

Be specific, data-driven, and focus on business value. Use the actual data to support your insights."""
            
            explanation = llm.generate(analysis_prompt, "You are a senior data analyst providing business insights from charts. Focus on actionable recommendations for decision-making.")
        except Exception as e:
            print(f"Error generating explanation: {e}")
            explanation = intent.get("explanation", "Chart analysis: This chart displays the selected metrics. Review the data to identify trends and patterns for informed decision-making.")
        
        return {
            "success": True,
            "action": "explain_chart",
            "chart_id": chart_id,
            "explanation": explanation,
            "insights": explanation  # For frontend to display
        }
    
    @staticmethod
    def _generate_answer_question(
        dashboard: Dict[str, Any],
        parameters: Dict[str, Any],
        intent: Dict[str, Any],
        available_columns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Answer questions about the data using Gemini with full dashboard and data context."""
        import pandas as pd
        import json
        from ai_agent.llm.gemini_client import GeminiClient
        from backend.config import settings
        
        question = parameters.get("question", "") or intent.get("explanation", "")
        
        # Get dataset data
        dataset_data = dashboard.get("_dataset_data", [])
        
        if not dataset_data:
            return {
                "success": False,
                "error": "No data available",
                "explanation": "I need data to answer your question. Please ensure your dataset is loaded."
            }
        
        # Always use Gemini for Q&A
        try:
            llm = GeminiClient()
        except Exception as e:
            return {
                "success": False,
                "error": "Gemini not available",
                "explanation": f"Gemini is required for Q&A but is not available: {str(e)}. Please configure Gemini API key."
            }
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(dataset_data)
            
            # Perform data analysis based on question
            analysis_results = {}
            question_lower = question.lower()
            
            # Extract column names
            column_names = [col.get("name", "") for col in available_columns]
            numeric_cols = [col.get("name", "") for col in available_columns if col.get("type") == "numeric"]
            string_cols = [col.get("name", "") for col in available_columns if col.get("type") == "string"]
            
            # Handle different question types
            if "top" in question_lower or "highest" in question_lower or "best" in question_lower:
                # Find top N items
                import re
                top_match = re.search(r'top\s+(\d+)', question_lower)
                n = int(top_match.group(1)) if top_match else 5
                
                # Try to find metric and category from question
                metric_col = None
                category_col = None
                
                for col in numeric_cols:
                    if col.lower() in question_lower:
                        metric_col = col
                        break
                
                for col in string_cols:
                    if col.lower() in question_lower:
                        category_col = col
                        break
                
                if not metric_col and numeric_cols:
                    metric_col = numeric_cols[0]
                if not category_col and string_cols:
                    category_col = string_cols[0]
                
                if metric_col and category_col and metric_col in df.columns and category_col in df.columns:
                    top_data = df.groupby(category_col)[metric_col].sum().sort_values(ascending=False).head(n)
                    analysis_results["top_items"] = top_data.to_dict()
                    analysis_results["metric"] = metric_col
                    analysis_results["category"] = category_col
                elif metric_col and metric_col in df.columns:
                    top_data = df.nlargest(n, metric_col)[[metric_col]]
                    analysis_results["top_items"] = top_data[metric_col].to_dict()
                    analysis_results["metric"] = metric_col
            
            elif "average" in question_lower or "mean" in question_lower or "avg" in question_lower:
                # Calculate average
                for col in numeric_cols:
                    if col.lower() in question_lower and col in df.columns:
                        avg_value = df[col].mean()
                        analysis_results["average"] = {col: avg_value}
                        break
                if not analysis_results.get("average") and numeric_cols:
                    col = numeric_cols[0]
                    if col in df.columns:
                        analysis_results["average"] = {col: df[col].mean()}
            
            elif "total" in question_lower or "sum" in question_lower:
                # Calculate sum
                for col in numeric_cols:
                    if col.lower() in question_lower and col in df.columns:
                        total_value = df[col].sum()
                        analysis_results["total"] = {col: total_value}
                        break
                if not analysis_results.get("total") and numeric_cols:
                    col = numeric_cols[0]
                    if col in df.columns:
                        analysis_results["total"] = {col: df[col].sum()}
            
            elif "count" in question_lower or "how many" in question_lower or "number of" in question_lower:
                # Count records
                analysis_results["count"] = len(df)
                if "unique" in question_lower or "distinct" in question_lower:
                    for col in column_names:
                        if col.lower() in question_lower and col in df.columns:
                            unique_count = df[col].nunique()
                            analysis_results["unique_count"] = {col: unique_count}
                            break
            
            elif "minimum" in question_lower or "min" in question_lower or "lowest" in question_lower:
                # Find minimum
                for col in numeric_cols:
                    if col.lower() in question_lower and col in df.columns:
                        min_value = df[col].min()
                        min_row = df.loc[df[col].idxmin()]
                        analysis_results["minimum"] = {col: min_value, "row": min_row.to_dict()}
                        break
            
            elif "maximum" in question_lower or "max" in question_lower:
                # Find maximum
                for col in numeric_cols:
                    if col.lower() in question_lower and col in df.columns:
                        max_value = df[col].max()
                        max_row = df.loc[df[col].idxmax()]
                        analysis_results["maximum"] = {col: max_value, "row": max_row.to_dict()}
                        break
            
            else:
                # General statistics
                if numeric_cols:
                    stats = df[numeric_cols].describe()
                    analysis_results["statistics"] = stats.to_dict()
            
            # Add basic dataset info
            analysis_results["dataset_info"] = {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": list(df.columns)
            }
            
            # Build comprehensive context for Gemini
            # Include dashboard widgets context
            dashboard_components = dashboard.get("components", [])
            widgets_summary = []
            for comp in dashboard_components:
                comp_info = {
                    "type": comp.get("type", "unknown"),
                    "title": comp.get("title", "Untitled")
                }
                config = comp.get("config", {})
                if config.get("x_axis"):
                    comp_info["x_axis"] = config.get("x_axis")
                if config.get("y_axis"):
                    comp_info["y_axis"] = config.get("y_axis")
                widgets_summary.append(comp_info)
            
            # Prepare data summary for Gemini (sample of actual data)
            data_sample = dataset_data[:50]  # Sample for context
            data_summary = {
                "total_rows": len(df),
                "sample_data": data_sample,
                "column_statistics": {}
            }
            
            # Add statistics for numeric columns
            for col in numeric_cols:
                if col in df.columns:
                    data_summary["column_statistics"][col] = {
                        "mean": float(df[col].mean()),
                        "median": float(df[col].median()),
                        "min": float(df[col].min()),
                        "max": float(df[col].max()),
                        "sum": float(df[col].sum()),
                        "std": float(df[col].std())
                    }
            
            # Add value counts for string columns (top 10)
            for col in string_cols:
                if col in df.columns:
                    value_counts = df[col].value_counts().head(10).to_dict()
                    data_summary["column_statistics"][col] = {
                        "unique_count": int(df[col].nunique()),
                        "top_values": {str(k): int(v) for k, v in value_counts.items()}
                    }
            
            # Use Gemini to generate comprehensive answer with insights
            try:
                # Build rich context for Gemini
                context_prompt = f"""You are an expert data analyst assistant helping users understand their dashboard data.

DASHBOARD CONTEXT:
- Current widgets: {json.dumps(widgets_summary, indent=2)}
- Total data rows: {len(df)}
- Available columns: {', '.join(column_names)}

DATA SUMMARY:
{json.dumps(data_summary, indent=2, default=str)}

DATA ANALYSIS RESULTS:
{json.dumps(analysis_results, indent=2, default=str)}

SAMPLE DATA (first 10 rows):
{json.dumps(data_sample[:10], indent=2, default=str)}

USER QUESTION: "{question}"

INSTRUCTIONS:
1. Answer the user's question directly and clearly using the actual data
2. Provide specific numbers, percentages, and insights from the data
3. If the question asks for a list (like "top 5"), provide the complete list with values
4. Include relevant insights and patterns you notice in the data
5. Reference the dashboard widgets if relevant to the question
6. Format numbers appropriately (use commas, percentages where relevant)
7. Be conversational but professional
8. If you notice interesting patterns or anomalies, mention them

Provide a comprehensive answer with insights:"""
                
                system_prompt = """You are a senior data analyst with expertise in business intelligence and data visualization. 
You help users understand their data by providing clear, accurate, and insightful answers based on actual data analysis.
You always reference specific numbers and data points, and provide actionable insights when relevant."""
                
                answer = llm.generate(context_prompt, system_prompt)
                
            except Exception as e:
                print(f"Error generating LLM answer: {e}")
                # Fallback: create answer from analysis results
                answer = f"Based on the data analysis:\n\n"
                if "top_items" in analysis_results:
                    answer += f"Top items by {analysis_results.get('metric', 'value')}:\n"
                    for item, value in list(analysis_results["top_items"].items())[:10]:
                        answer += f"- {item}: {value:,.2f}\n"
                elif "average" in analysis_results:
                    for col, val in analysis_results["average"].items():
                        answer += f"Average {col}: {val:,.2f}\n"
                elif "total" in analysis_results:
                    for col, val in analysis_results["total"].items():
                        answer += f"Total {col}: {val:,.2f}\n"
                elif "count" in analysis_results:
                    answer += f"Total records: {analysis_results['count']:,}\n"
                else:
                    answer += json.dumps(analysis_results, indent=2, default=str)
            
            return {
                "success": True,
                "action": "answer_question",
                "question": question,
                "explanation": answer,
                "analysis": analysis_results  # Include raw analysis for debugging
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error in answer_question: {error_trace}")
            return {
                "success": False,
                "error": str(e),
                "explanation": f"I encountered an error analyzing the data: {str(e)}. Please try rephrasing your question or check that your data is properly loaded."
            }
