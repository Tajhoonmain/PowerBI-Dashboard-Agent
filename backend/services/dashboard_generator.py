"""Dashboard auto-generation service."""
import pandas as pd
from typing import List, Dict, Any
import uuid


class DashboardGenerator:
    """Service for auto-generating dashboards from datasets."""
    
    @staticmethod
    def generate_dashboard(
        df: pd.DataFrame,
        columns: List[Dict[str, Any]],
        title: str = "Dashboard"
    ) -> Dict[str, Any]:
        """
        Auto-generate a dashboard from a dataset.
        
        Returns: Dashboard configuration dictionary
        """
        components = []
        
        # Identify column types - column names should match after cleaning
        numeric_cols = []
        string_cols = []
        date_cols = []
        
        for col_meta in columns:
            col_name = col_meta.get('name', '')
            # Verify column exists in DataFrame
            if col_name not in df.columns:
                continue  # Skip if column not found
            
            col_type = col_meta.get('type', 'string')
            if col_type == 'numeric':
                numeric_cols.append(col_name)
            elif col_type == 'string':
                string_cols.append(col_name)
            elif col_type == 'date':
                date_cols.append(col_name)
        
        # Generate KPI cards for numeric columns (top 3)
        for i, col in enumerate(numeric_cols[:3]):
            try:
                if col in df.columns and len(df) > 0:
                    kpi_value = float(df[col].sum())
                else:
                    kpi_value = 0
            except (KeyError, TypeError, ValueError) as e:
                print(f"Warning: Could not calculate KPI for {col}: {e}")
                kpi_value = 0
            components.append({
                "id": str(uuid.uuid4()),
                "type": "kpi",
                "title": col.replace('_', ' ').title(),
                "config": {
                    "column": col,
                    "value": kpi_value,
                    "format": "number"
                },
                "position": {"row": 0, "col": i, "width": 1, "height": 1}
            })
        
        # Generate bar chart (first numeric vs first string, if available)
        if numeric_cols and string_cols:
            try:
                bar_col = string_cols[0]
                value_col = numeric_cols[0]
                
                # Verify columns exist in DataFrame
                if bar_col in df.columns and value_col in df.columns:
                    # Aggregate data for bar chart
                    bar_data = df.groupby(bar_col)[value_col].sum().reset_index()
                    bar_data = bar_data.sort_values(value_col, ascending=False).head(10)
                    
                    # Convert to JSON-serializable format
                    bar_records = bar_data.to_dict('records')
                    # Ensure all values are JSON serializable
                    for record in bar_records:
                        for key, value in record.items():
                            if pd.isna(value):
                                record[key] = None
                            elif isinstance(value, (pd.Timestamp, pd.Timedelta)):
                                record[key] = str(value)
                            else:
                                try:
                                    record[key] = float(value) if isinstance(value, (int, float)) else str(value)
                                except:
                                    record[key] = str(value)
                    
                    components.append({
                        "id": str(uuid.uuid4()),
                        "type": "bar_chart",
                        "title": f"{value_col.replace('_', ' ').title()} by {bar_col.replace('_', ' ').title()}",
                        "config": {
                            "x_axis": bar_col,
                            "y_axis": value_col,
                            "aggregation": "sum",
                            "data": bar_records
                        },
                        "position": {"row": 1, "col": 0, "width": 2, "height": 2}
                    })
            except Exception as e:
                # Skip bar chart if there's an error
                print(f"Warning: Could not generate bar chart: {e}")
        
        # Generate line chart (if date column exists)
        if date_cols and numeric_cols:
            try:
                date_col = date_cols[0]
                value_col = numeric_cols[0]
                
                # Verify columns exist
                if date_col in df.columns and value_col in df.columns:
                    # Ensure date column is datetime
                    df_temp = df.copy()
                    df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                    df_temp = df_temp.dropna(subset=[date_col])
                    
                    if len(df_temp) > 0:
                        # Group by date
                        line_data = df_temp.groupby(df_temp[date_col].dt.date)[value_col].sum().reset_index()
                        line_data.columns = [date_col, value_col]
                        line_data = line_data.sort_values(date_col)
                        
                        # Convert to JSON-serializable format
                        line_records = line_data.to_dict('records')
                        # Ensure all values are JSON serializable
                        for record in line_records:
                            for key, value in record.items():
                                if pd.isna(value):
                                    record[key] = None
                                elif isinstance(value, (pd.Timestamp, pd.Timedelta, pd._libs.tslibs.timestamps.Timestamp)):
                                    record[key] = str(value)
                                elif isinstance(value, (int, float)):
                                    record[key] = float(value)
                                else:
                                    record[key] = str(value)
                        
                        components.append({
                            "id": str(uuid.uuid4()),
                            "type": "line_chart",
                            "title": f"{value_col.replace('_', ' ').title()} Over Time",
                            "config": {
                                "x_axis": date_col,
                                "y_axis": value_col,
                                "aggregation": "sum",
                                "data": line_records
                            },
                            "position": {"row": 1, "col": 2, "width": 2, "height": 2}
                        })
            except Exception as e:
                # Skip line chart if there's an error
                print(f"Warning: Could not generate line chart: {e}")
        
        # Generate data table (first 100 rows)
        try:
            table_df = df.head(100)
            table_data = table_df.to_dict('records')
            # Use actual DataFrame column names
            table_columns = list(df.columns)
            
            # Ensure all values are JSON serializable
            for record in table_data:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                    elif isinstance(value, (pd.Timestamp, pd.Timedelta)):
                        record[key] = str(value)
                    elif isinstance(value, (int, float)):
                        record[key] = float(value) if not pd.isna(value) else None
                    else:
                        record[key] = str(value) if value is not None else None
            
            components.append({
                "id": str(uuid.uuid4()),
                "type": "table",
                "title": "Data Table",
                "config": {
                    "columns": table_columns,
                    "data": table_data,
                    "page_size": 10
                },
                "position": {"row": 3, "col": 0, "width": 4, "height": 3}
            })
        except Exception as e:
            print(f"Warning: Could not generate data table: {e}")
        
        # Ensure at least one component exists
        if not components:
            # Add a simple message component if no components could be generated
            components.append({
                "id": str(uuid.uuid4()),
                "type": "kpi",
                "title": "No Data",
                "config": {
                    "column": None,
                    "value": 0,
                    "format": "number"
                },
                "position": {"row": 0, "col": 0, "width": 1, "height": 1}
            })
        
        # Generate layout
        layout = {
            "rows": 6,
            "cols": 4,
            "grid": [comp["position"] for comp in components]
        }
        
        return {
            "title": title,
            "components": components,
            "layout": layout
        }
    
    @staticmethod
    def update_component(
        dashboard: Dict[str, Any],
        component_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a dashboard component."""
        for i, comp in enumerate(dashboard['components']):
            if comp['id'] == component_id:
                dashboard['components'][i].update(updates)
                break
        return dashboard
    
    @staticmethod
    def add_component(
        dashboard: Dict[str, Any],
        component: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new component to the dashboard."""
        dashboard['components'].append(component)
        dashboard['layout']['grid'].append(component.get('position', {}))
        return dashboard
    
    @staticmethod
    def remove_component(
        dashboard: Dict[str, Any],
        component_id: str
    ) -> Dict[str, Any]:
        """Remove a component from the dashboard."""
        dashboard['components'] = [
            comp for comp in dashboard['components'] if comp['id'] != component_id
        ]
        dashboard['layout']['grid'] = [
            pos for pos in dashboard['layout']['grid']
            if any(comp['id'] == component_id for comp in dashboard['components'])
        ]
        return dashboard

