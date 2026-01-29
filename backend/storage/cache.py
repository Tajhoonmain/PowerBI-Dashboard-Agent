"""Data caching utilities."""
import os
import pickle
import hashlib
import pandas as pd
from typing import Optional
from backend.config import settings


def get_cache_key(dataset_id: str, transformation_steps: list) -> str:
    """Generate cache key from dataset ID and transformation steps."""
    key_string = f"{dataset_id}_{str(transformation_steps)}"
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_dataframe(df: pd.DataFrame, cache_key: str) -> str:
    """Cache a DataFrame to disk."""
    os.makedirs(settings.cache_dir, exist_ok=True)
    cache_path = os.path.join(settings.cache_dir, f"{cache_key}.pkl")
    
    with open(cache_path, 'wb') as f:
        pickle.dump(df, f)
    
    return cache_path


def load_cached_dataframe(cache_key: str) -> Optional[pd.DataFrame]:
    """Load a cached DataFrame from disk."""
    cache_path = os.path.join(settings.cache_dir, f"{cache_key}.pkl")
    
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None


def clear_cache(cache_key: Optional[str] = None):
    """Clear cache for a specific key or all cache."""
    if cache_key:
        cache_path = os.path.join(settings.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_path):
            os.remove(cache_path)
    else:
        # Clear all cache
        if os.path.exists(settings.cache_dir):
            for file in os.listdir(settings.cache_dir):
                if file.endswith('.pkl'):
                    os.remove(os.path.join(settings.cache_dir, file))


