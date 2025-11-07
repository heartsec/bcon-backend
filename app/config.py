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
    
    # Dify Configuration
    dify_api_key: str = ""  # Dify API 密钥
    dify_base_url: str = "https://api.dify.ai/v1"  # Dify API 基础 URL (云版本使用默认值)
    dify_app_id: str = ""  # Dify App ID (可选，用于特定应用)
    
    # Dify Workflow 输出变量配置
    # 在这里维护您的 Dify workflow 输出的所有变量名
    dify_output_variables: list[str] = [
        "confirmation_record",    # 确认记录 (主要输出)
        "extracted_data",       # 提取的数据
        "baseline_data",        # 基线数据
        # 添加其他变量示例:
        # "document_type",        # 文档类型
        # "extracted_data",       # 提取的数据
        # "validation_result",    # 验证结果
        # "confidence_score",     # 置信度分数
        # "processing_status",    # 处理状态
    ]

    model_config = ConfigDict(env_file=".env", case_sensitive=False)
    # Logging Configuration
    log_level: str = model_config.get("LOG_LEVEL", "INFO")
    


settings = Settings()
