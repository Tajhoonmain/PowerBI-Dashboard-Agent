"""Transformation engine for Power Query-like operations."""
import pandas as pd
from typing import List, Dict, Any, Optional
from backend.storage.cache import get_cache_key, cache_dataframe, load_cached_dataframe


class TransformationService:
    """Service for applying data transformations."""
    
    @staticmethod
    def apply_transformations(
        df: pd.DataFrame,
        steps: List[Dict[str, Any]],
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Apply a list of transformation steps to a DataFrame.
        
        Args:
            df: Input DataFrame
            steps: List of transformation step dictionaries
            use_cache: Whether to use caching
        
        Returns: Transformed DataFrame
        """
        # Check cache
        if use_cache and steps:
            cache_key = get_cache_key("transformed", steps)
            cached_df = load_cached_dataframe(cache_key)
            if cached_df is not None:
                return cached_df
        
        # Sort steps by order
        sorted_steps = sorted(steps, key=lambda x: x.get('order', 0))
        
        result_df = df.copy()
        
        # Apply each transformation
        for step in sorted_steps:
            step_type = step.get('step_type')
            parameters = step.get('parameters', {})
            
            result_df = TransformationService._apply_single_transformation(
                result_df, step_type, parameters
            )
        
        # Cache result
        if use_cache and steps:
            cache_key = get_cache_key("transformed", steps)
            cache_dataframe(result_df, cache_key)
        
        return result_df
    
    @staticmethod
    def _apply_single_transformation(
        df: pd.DataFrame,
        step_type: str,
        parameters: Dict[str, Any]
    ) -> pd.DataFrame:
        """Apply a single transformation step."""
        if step_type == 'cast':
            return TransformationService._cast_type(df, parameters)
        elif step_type == 'filter':
            return TransformationService._filter_rows(df, parameters)
        elif step_type == 'rename':
            return TransformationService._rename_column(df, parameters)
        elif step_type == 'remove_nulls':
            return TransformationService._remove_nulls(df, parameters)
        elif step_type == 'aggregate':
            return TransformationService._aggregate(df, parameters)
        else:
            raise ValueError(f"Unknown transformation type: {step_type}")
    
    @staticmethod
    def _cast_type(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Cast column to specified type."""
        column = params.get('column')
        target_type = params.get('target_type')
        
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found")
        
        result_df = df.copy()
        
        if target_type == 'numeric':
            result_df[column] = pd.to_numeric(result_df[column], errors='coerce')
        elif target_type == 'string':
            result_df[column] = result_df[column].astype(str)
        elif target_type == 'date':
            result_df[column] = pd.to_datetime(result_df[column], errors='coerce')
        elif target_type == 'boolean':
            result_df[column] = result_df[column].astype(bool)
        
        return result_df
    
    @staticmethod
    def _filter_rows(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Filter rows based on condition."""
        column = params.get('column')
        operator = params.get('operator')  # 'eq', 'gt', 'lt', 'contains', etc.
        value = params.get('value')
        
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found")
        
        result_df = df.copy()
        
        if operator == 'eq':
            result_df = result_df[result_df[column] == value]
        elif operator == 'gt':
            result_df = result_df[result_df[column] > value]
        elif operator == 'lt':
            result_df = result_df[result_df[column] < value]
        elif operator == 'gte':
            result_df = result_df[result_df[column] >= value]
        elif operator == 'lte':
            result_df = result_df[result_df[column] <= value]
        elif operator == 'contains':
            result_df = result_df[result_df[column].astype(str).str.contains(str(value), case=False, na=False)]
        elif operator == 'in':
            result_df = result_df[result_df[column].isin(value)]
        
        return result_df
    
    @staticmethod
    def _rename_column(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Rename a column."""
        old_name = params.get('old_name')
        new_name = params.get('new_name')
        
        if old_name not in df.columns:
            raise ValueError(f"Column '{old_name}' not found")
        
        result_df = df.copy()
        result_df.rename(columns={old_name: new_name}, inplace=True)
        return result_df
    
    @staticmethod
    def _remove_nulls(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Remove null values."""
        column = params.get('column')
        
        result_df = df.copy()
        
        if column:
            # Remove nulls from specific column
            result_df = result_df[result_df[column].notna()]
        else:
            # Remove rows with any nulls
            result_df = result_df.dropna()
        
        return result_df
    
    @staticmethod
    def _aggregate(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Aggregate data."""
        group_by = params.get('group_by', [])
        agg_func = params.get('agg_func', 'sum')  # sum, mean, count, etc.
        agg_column = params.get('agg_column')
        
        result_df = df.copy()
        
        if not group_by:
            # Simple aggregation without grouping
            if agg_column:
                if agg_func == 'sum':
                    return pd.DataFrame({agg_column: [result_df[agg_column].sum()]})
                elif agg_func == 'mean':
                    return pd.DataFrame({agg_column: [result_df[agg_column].mean()]})
                elif agg_func == 'count':
                    return pd.DataFrame({agg_column: [len(result_df)]})
        else:
            # Group by aggregation
            if agg_column:
                if agg_func == 'sum':
                    return result_df.groupby(group_by)[agg_column].sum().reset_index()
                elif agg_func == 'mean':
                    return result_df.groupby(group_by)[agg_column].mean().reset_index()
                elif agg_func == 'count':
                    return result_df.groupby(group_by)[agg_column].count().reset_index()
            else:
                # Count by group
                return result_df.groupby(group_by).size().reset_index(name='count')
        
        return result_df


