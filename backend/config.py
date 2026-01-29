"""Configuration settings for the application."""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "sqlite:///./database/bi_dashboard.db"
    
    # LLM Configuration
    llm_provider: str = "gemini"  # "ollama", "huggingface", or "gemini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    hf_model_name: str = "google/flan-t5-base"
    gemini_api_key: str = ""  # Set via GEMINI_API_KEY env var
    gemini_model: str = "gemini-2.5-flash"  # Use gemini-2.5-flash, gemini-1.5-flash, or gemini-1.5-pro
    
    # Power BI REST API Configuration
    powerbi_enabled: bool = False  # Set to True to enable Power BI API
    powerbi_tenant_id: str = ""  # Azure AD Tenant ID
    powerbi_client_id: str = ""  # Azure AD App Registration Client ID
    powerbi_client_secret: str = ""  # Azure AD App Registration Client Secret
    powerbi_workspace_id: str = ""  # Power BI Workspace ID (optional, uses "My Workspace" if empty)
    
    # File Storage
    upload_dir: str = "./data/uploads"
    cache_dir: str = "./data/cache"
    max_upload_size: int = 10485760  # 10MB
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:8050,http://localhost:5173,http://127.0.0.1:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Create directories if they don't exist
settings = Settings()
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.cache_dir, exist_ok=True)
os.makedirs("database", exist_ok=True)

