from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # RustFS/S3 Configuration
    rustfs_endpoint: str = "http://localhost:9000"
    rustfs_access_key: str = "rustfsadmin"
    rustfs_secret_key: str = "rustfssecret"
    rustfs_bucket_name: str = "pdf-processing"
    rustfs_region: str = "us-east-1"  # RustFS doesn't validate region
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
