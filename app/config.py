from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # RustFS/S3 Configuration
    rustfs_endpoint: str
    rustfs_access_key: str
    rustfs_secret_key: str
    rustfs_bucket_name: str
    rustfs_region: str = "us-east-1"  # RustFS doesn't validate region
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
