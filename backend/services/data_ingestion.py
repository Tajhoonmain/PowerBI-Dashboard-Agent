"""Data ingestion service for processing uploaded files."""
import pandas as pd
import os
from typing import Dict, Any, Tuple
from backend.utils.schema_detector import detect_schema
from backend.storage.file_manager import save_uploaded_file


class DataIngestionService:
    """Service for ingesting and processing data files."""
    
    @staticmethod
    def process_file(file_content: bytes, filename: str) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
        """
        Process uploaded file and return DataFrame, schema, and file path.
        
        Returns: (dataframe, schema_dict, file_path)
        """
        # Save file
        file_path = save_uploaded_file(file_content, filename)
        
        # Basic validation - check file exists and size
        if not os.path.exists(file_path):
            raise ValueError("File not found after upload")
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            os.remove(file_path)
            raise ValueError("File is empty")
        
        # Read file based on extension
        file_ext = os.path.splitext(filename)[1].lower()
        
        try:
            if file_ext == '.csv':
                # Try different encodings and separators
                df = None
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                separators = [',', ';', '\t']
                
                for encoding in encodings:
                    for sep in separators:
                        try:
                            # Try with error_bad_lines parameter (pandas < 1.3) or on_bad_lines (pandas >= 1.3)
                            try:
                                test_df = pd.read_csv(file_path, encoding=encoding, sep=sep, on_bad_lines='skip')
                            except TypeError:
                                # Older pandas version
                                test_df = pd.read_csv(file_path, encoding=encoding, sep=sep, error_bad_lines=False, warn_bad_lines=False)
                            
                            if not test_df.empty and len(test_df.columns) > 0:
                                df = test_df
                                break
                        except (UnicodeDecodeError, pd.errors.EmptyDataError, pd.errors.ParserError, Exception):
                            continue
                    if df is not None and not df.empty:
                        break
                
                # If still None, try default read_csv
                if df is None:
                    try:
                        try:
                            df = pd.read_csv(file_path, on_bad_lines='skip')
                        except TypeError:
                            df = pd.read_csv(file_path, error_bad_lines=False, warn_bad_lines=False)
                    except Exception as e:
                        raise ValueError(f"Could not read CSV file: {str(e)}")
                
                if df is None or df.empty:
                    raise ValueError("File contains no data rows. CSV must have at least one row after the header.")
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                os.remove(file_path)
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Check if DataFrame is empty
            if df.empty:
                os.remove(file_path)
                raise ValueError("File contains no data rows. CSV must have at least one row after the header.")
            
            # Check if DataFrame has no columns
            if len(df.columns) == 0:
                os.remove(file_path)
                raise ValueError("File contains no columns. Please check your file format.")
            
            # Clean column names (remove spaces, special chars)
            df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
            
            # Detect schema
            schema = detect_schema(df)
            
            # Prepare metadata
            metadata = {
                "filename": filename,
                "file_path": file_path,
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": schema,
            }
            
            return df, metadata, file_path
            
        except Exception as e:
            # Clean up file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValueError(f"Error processing file: {str(e)}")
    
    @staticmethod
    def load_dataset(file_path: str) -> pd.DataFrame:
        """Load dataset from file path."""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Clean column names to match what was done during upload
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
        
        return df

