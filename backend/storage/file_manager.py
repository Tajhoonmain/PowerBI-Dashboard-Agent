"""File management utilities."""
import os
import shutil
from pathlib import Path
from typing import Optional
from backend.config import settings


def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """
    Save uploaded file to storage directory.
    
    Returns: Path to saved file
    """
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Generate unique filename to avoid conflicts
    file_path = os.path.join(settings.upload_dir, filename)
    counter = 1
    base_name, ext = os.path.splitext(filename)
    
    while os.path.exists(file_path):
        file_path = os.path.join(settings.upload_dir, f"{base_name}_{counter}{ext}")
        counter += 1
    
    # Write file
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    return file_path


def get_file_path(filename: str) -> Optional[str]:
    """Get full path to a file in upload directory."""
    file_path = os.path.join(settings.upload_dir, filename)
    if os.path.exists(file_path):
        return file_path
    return None


def delete_file(file_path: str) -> bool:
    """Delete a file from storage."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


