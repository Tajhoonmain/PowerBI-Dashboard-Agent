"""Schema detection utilities for datasets."""
import pandas as pd
from typing import List, Dict, Any
from backend.utils.data_types import detect_data_type, get_column_statistics


def detect_schema(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Detect schema for all columns in a DataFrame.
    
    Returns a list of column metadata dictionaries.
    """
    columns = []
    
    for col in df.columns:
        dtype = detect_data_type(df[col])
        stats = get_column_statistics(df[col], dtype)
        
        # Get sample values (non-null)
        sample_values = df[col].dropna().head(5).tolist()
        # Convert to native Python types
        sample_values = [str(v) if pd.notna(v) else None for v in sample_values]
        
        column_info = {
            "name": str(col),
            "type": dtype,
            "null_count": stats["null_count"],
            "null_percentage": stats["null_percentage"],
            "unique_count": stats["unique_count"],
            "sample_values": sample_values,
            **{k: v for k, v in stats.items() if k not in ["null_count", "null_percentage", "unique_count"]}
        }
        
        columns.append(column_info)
    
    return columns


