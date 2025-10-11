from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from pathlib import Path
import os
import base64
import json


class Settings(BaseSettings):
    """Application configuration settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "TikTok Scraper"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    STREAMLIT_PORT: int = 8501
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./tiktok_scraper.db"
    
    # Google Drive
    GOOGLE_DRIVE_CREDENTIALS_FILE: str = "./credentials/credentials.json"
    GOOGLE_DRIVE_TOKEN_FILE: str = "./credentials/token.pickle"
    GOOGLE_DRIVE_ROOT_FOLDER_ID: Optional[str] = None
    GOOGLE_DRIVE_CREDENTIALS_BASE64: Optional[str] = None  # For cloud deployment
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = None  # Specific folder ID for uploads
    
    # TikTok Scraping
    TIKTOK_MAX_VIDEOS_PER_REQUEST: int = 50
    TIKTOK_REQUEST_DELAY_MIN: float = 1.0
    TIKTOK_REQUEST_DELAY_MAX: float = 3.0
    TIKTOK_MAX_RETRIES: int = 3
    TIKTOK_TIMEOUT: int = 30
    TIKTOK_USE_PLAYWRIGHT_FALLBACK: bool = True
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    # Proxy
    USE_PROXY: bool = False
    PROXY_URL: Optional[str] = None
    PROXY_ROTATION_ENABLED: bool = False
    
    # External API for No-Watermark
    NOWATERMARK_API_KEY: Optional[str] = None
    NOWATERMARK_API_URL: Optional[str] = None
    
    # Celery/Redis
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Scheduling
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_DEFAULT_INTERVAL_MINUTES: int = 60
    
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: str = "your-secret-api-key-here"
    
    # Storage
    LOCAL_STORAGE_PATH: str = "./downloads"
    MAX_CONCURRENT_DOWNLOADS: int = 5
    
    @property
    def api_keys_list(self) -> List[str]:
        """Parse API keys from comma-separated string"""
        return [key.strip() for key in self.API_KEYS.split(",") if key.strip()]
    
    @property
    def local_storage_path_obj(self) -> Path:
        """Get local storage path as Path object"""
        path = Path(self.LOCAL_STORAGE_PATH)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def credentials_path(self) -> Path:
        """Get credentials directory path"""
        path = Path("credentials")
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def setup_cloud_credentials(self):
        """Setup Google Drive credentials from base64 environment variable (for cloud deployment)"""
        if self.GOOGLE_DRIVE_CREDENTIALS_BASE64:
            try:
                # Decode base64 credentials
                credentials_json = base64.b64decode(self.GOOGLE_DRIVE_CREDENTIALS_BASE64).decode('utf-8')
                
                # Parse JSON to validate
                credentials_data = json.loads(credentials_json)
                
                # Save to file
                credentials_path = Path(self.GOOGLE_DRIVE_CREDENTIALS_FILE)
                credentials_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(credentials_path, 'w') as f:
                    json.dump(credentials_data, f, indent=2)
                
                print(f"✓ Google Drive credentials decoded and saved to {credentials_path}")
                return True
            except Exception as e:
                print(f"✗ Failed to decode Google Drive credentials: {e}")
                return False
        return False


# Global settings instance
settings = Settings()

# Setup cloud credentials if available
settings.setup_cloud_credentials()
