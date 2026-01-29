"""Data type detection and validation utilities."""
import pandas as pd
import numpy as np
from typing import Any, Dict


def detect_data_type(series: pd.Series) -> str:
    """
    Detect the data type of a pandas Series.
    
    Returns: 'numeric', 'string', 'date', 'boolean'
    """
    # Check for boolean
    if series.dtype == bool or series.dtype.name == 'bool':
        return 'boolean'
    
    # Check for datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return 'date'
    
    # Check for numeric
    if pd.api.types.is_numeric_dtype(series):
        return 'numeric'
    
    # Check if string can be converted to date
    if series.dtype == 'object':
        # Try to parse as date
        try:
            pd.to_datetime(series.dropna().head(100), errors='coerce', format='mixed')
            return 'date'
        except (ValueError, TypeError):
            pass
    
    # Default to string
    return 'string'


def get_column_statistics(series: pd.Series, dtype: str) -> Dict[str, Any]:
    """Get statistics for a column based on its type."""
    stats = {
        "null_count": int(series.isna().sum()),
        "null_percentage": float((series.isna().sum() / len(series)) * 100),
        "unique_count": int(series.nunique()),
    }
    
    if dtype == 'numeric':
        stats.update({
            "min": float(series.min()) if not series.empty else None,
            "max": float(series.max()) if not series.empty else None,
            "mean": float(series.mean()) if not series.empty else None,
            "median": float(series.median()) if not series.empty else None,
            "std": float(series.std()) if not series.empty else None,
        })
    elif dtype == 'date':
        stats.update({
            "min_date": str(series.min()) if not series.empty else None,
            "max_date": str(series.max()) if not series.empty else None,
        })
    elif dtype == 'string':
        stats.update({
            "min_length": int(series.astype(str).str.len().min()) if not series.empty else None,
            "max_length": int(series.astype(str).str.len().max()) if not series.empty else None,
            "avg_length": float(series.astype(str).str.len().mean()) if not series.empty else None,
        })
    
    return stats

