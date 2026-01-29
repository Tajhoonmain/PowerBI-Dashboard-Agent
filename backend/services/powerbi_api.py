"""Power BI REST API service for creating dashboards programmatically."""
import requests
import msal
from typing import Dict, Any, Optional, List
import json
from backend.config import settings


class PowerBIClient:
    """Client for Power BI REST API operations."""
    
    def __init__(self):
        """Initialize Power BI client with authentication."""
        if not settings.powerbi_enabled:
            raise ValueError("Power BI API is not enabled. Set POWERBI_ENABLED=true in .env")
        
        self.tenant_id = settings.powerbi_tenant_id
        self.client_id = settings.powerbi_client_id
        self.client_secret = settings.powerbi_client_secret
        self.workspace_id = settings.powerbi_workspace_id or "me"  # "me" = My Workspace
        
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError("Power BI credentials not configured. Set POWERBI_TENANT_ID, POWERBI_CLIENT_ID, and POWERBI_CLIENT_SECRET in .env")
        
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        self.access_token = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Azure AD and get access token."""
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret
        )
        
        # Request token for Power BI
        result = app.acquire_token_for_client(scopes=["https://analysis.windows.net/powerbi/api/.default"])
        
        if "access_token" in result:
            self.access_token = result["access_token"]
        else:
            raise ValueError(f"Failed to authenticate with Power BI: {result.get('error_description', 'Unknown error')}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def create_dataset(self, dataset_name: str, tables: List[Dict[str, Any]]) -> str:
        """Create a dataset in Power BI."""
        url = f"{self.base_url}/groups/{self.workspace_id}/datasets"
        
        dataset_def = {
            "name": dataset_name,
            "tables": tables,
            "defaultMode": "Import"
        }
        
        response = requests.post(url, headers=self._get_headers(), json=dataset_def)
        response.raise_for_status()
        
        dataset_id = response.json().get("id")
        return dataset_id
    
    def push_data(self, dataset_id: str, table_name: str, rows: List[Dict[str, Any]]):
        """Push data rows to a table in a dataset."""
        url = f"{self.base_url}/groups/{self.workspace_id}/datasets/{dataset_id}/tables/{table_name}/rows"
        
        payload = {"rows": rows}
        
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
    
    def create_report(self, dataset_id: str, report_name: str, visuals: List[Dict[str, Any]]) -> str:
        """Create a report with visuals in Power BI."""
        # Power BI REST API doesn't directly support creating reports with visuals
        # We need to use the report generation API or create a .pbix and import it
        # For now, we'll create a basic report structure
        
        url = f"{self.base_url}/groups/{self.workspace_id}/reports"
        
        # Create report definition
        report_def = {
            "name": report_name,
            "datasetId": dataset_id
        }
        
        # Note: Creating reports with visuals requires using the Import API with a .pbix file
        # or using the Report Generation API (which is more complex)
        # For now, we'll return instructions to use the Import API
        
        return "report_creation_requires_pbix_import"
    
    def import_pbix_file(self, pbix_content: bytes, dataset_name: str, name_conflict: str = "Abort") -> Dict[str, Any]:
        """Import a .pbix file to Power BI using the Import API."""
        url = f"{self.base_url}/groups/{self.workspace_id}/imports"
        
        # Prepare multipart form data
        files = {
            'file': ('dashboard.pbix', pbix_content, 'application/octet-stream')
        }
        
        params = {
            'datasetDisplayName': dataset_name,
            'nameConflict': name_conflict
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        response = requests.post(url, headers=headers, files=files, params=params)
        response.raise_for_status()
        
        import_result = response.json()
        import_id = import_result.get("id")
        
        return {
            "import_id": import_id,
            "status": "InProgress",
            "message": "Import started. Use get_import_status to check progress."
        }
    
    def get_import_status(self, import_id: str) -> Dict[str, Any]:
        """Get the status of an import operation."""
        url = f"{self.base_url}/groups/{self.workspace_id}/imports/{import_id}"
        
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def create_report_from_dataset(self, dataset_id: str, report_name: str) -> str:
        """Create a basic report from a dataset (visuals need to be added manually or via .pbix import)."""
        # This creates an empty report - visuals would need to be added via .pbix import
        # or using Power BI's report generation capabilities
        
        # For now, return the dataset ID so user can create report manually
        # or we can use the Import API with a properly formatted .pbix
        return dataset_id


