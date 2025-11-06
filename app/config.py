from pydantic_settings import BaseSettings
from pydantic import ConfigDict


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
    
    # Cache Configuration
    cache_dir: str = "cache"  # 本地缓存目录
    cache_max_size_mb: int = 1024  # 缓存最大容量 (MB)
    cache_ttl_seconds: int = 3600  # 缓存过期时间 (秒)
    
    model_config = ConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
