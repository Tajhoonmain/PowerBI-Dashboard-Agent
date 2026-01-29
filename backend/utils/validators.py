"""Input validation utilities."""
import os
from pathlib import Path
from typing import Optional, Tuple
from backend.config import settings


def validate_file_upload(file_path: str, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file.
    
    Returns: (is_valid, error_message)
    """
    # Check file extension
    allowed_extensions = {'.csv', '.xlsx', '.xls'}
    file_ext = Path(filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    # Check file size
    if not os.path.exists(file_path):
        return False, "File not found"
    
    file_size = os.path.getsize(file_path)
    if file_size > settings.max_upload_size:
        return False, f"File size exceeds maximum allowed size ({settings.max_upload_size} bytes)"
    
    if file_size == 0:
        return False, "File is empty"
    
    return True, None

