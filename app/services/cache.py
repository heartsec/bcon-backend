import os
import time
import hashlib
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, cache_dir: str, max_size_mb: int, ttl_seconds: int):
        """
        初始化缓存服务
        
        Args:
            cache_dir: 缓存目录路径
            max_size_mb: 缓存最大容量(MB)
            ttl_seconds: 缓存过期时间(秒)
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_seconds
        
        # 创建缓存目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Cache directory initialized: {self.cache_dir}")
    
    def _get_cache_key(self, file_path: str) -> str:
        """
        生成缓存键
        
        Args:
            file_path: 文件路径
            
        Returns:
            缓存键 (MD5 hash)
        """
        return hashlib.md5(file_path.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str, extension: str = "") -> Path:
        """
        获取缓存文件路径
        
        Args:
            cache_key: 缓存键
            extension: 文件扩展名
            
        Returns:
            缓存文件路径
        """
        return self.cache_dir / f"{cache_key}{extension}"
    
    def get(self, file_path: str, extension: str = "") -> Optional[Path]:
        """
        从缓存获取文件
        
        Args:
            file_path: 原始文件路径
            extension: 文件扩展名
            
        Returns:
            缓存文件路径，如果不存在或已过期则返回 None
        """
        cache_key = self._get_cache_key(file_path)
        cache_file = self._get_cache_file_path(cache_key, extension)
        
        if not cache_file.exists():
            logger.debug(f"Cache miss: {file_path}")
            return None
        
        # 检查是否过期
        file_age = time.time() - cache_file.stat().st_mtime
        if file_age > self.ttl_seconds:
            logger.info(f"Cache expired: {file_path}")
            cache_file.unlink()
            return None
        
        logger.debug(f"Cache hit: {file_path}")
        return cache_file
    
    def put(self, file_path: str, data: bytes, extension: str = "") -> Path:
        """
        将文件写入缓存
        
        Args:
            file_path: 原始文件路径
            data: 文件数据
            extension: 文件扩展名
            
        Returns:
            缓存文件路径
        """
        # 检查并清理缓存空间
        self._ensure_space(len(data))
        
        cache_key = self._get_cache_key(file_path)
        cache_file = self._get_cache_file_path(cache_key, extension)
        
        cache_file.write_bytes(data)
        logger.info(f"File cached: {file_path} -> {cache_file}")
        
        return cache_file
    
    def _ensure_space(self, required_bytes: int):
        """
        确保有足够的缓存空间
        
        Args:
            required_bytes: 需要的空间大小(字节)
        """
        current_size = self._get_cache_size()
        
        if current_size + required_bytes <= self.max_size_bytes:
            return
        
        logger.info("Cache size exceeded, cleaning old files...")
        
        # 获取所有缓存文件并按修改时间排序
        cache_files = sorted(
            self.cache_dir.glob("*"),
            key=lambda p: p.stat().st_mtime
        )
        
        # 删除最旧的文件直到有足够空间
        for file in cache_files:
            if current_size + required_bytes <= self.max_size_bytes:
                break
            
            if not file.is_file():
                continue
                
            file_size = file.stat().st_size
            file.unlink()
            current_size -= file_size
            logger.debug(f"Removed old cache file: {file}")
    
    def _get_cache_size(self) -> int:
        """
        获取当前缓存总大小
        
        Returns:
            缓存大小(字节)
        """
        return sum(f.stat().st_size for f in self.cache_dir.glob("*") if f.is_file())
    
    def clear(self):
        """清空所有缓存"""
        for file in self.cache_dir.glob("*"):
            if file.is_file():
                file.unlink()
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        files = list(self.cache_dir.glob("*"))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        
        return {
            "total_files": len([f for f in files if f.is_file()]),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "usage_percent": round((total_size / self.max_size_bytes) * 100, 2) if self.max_size_bytes > 0 else 0
        }


# 创建全局缓存服务实例
from app.config import settings
cache_service = CacheService(
    cache_dir=settings.cache_dir,
    max_size_mb=settings.cache_max_size_mb,
    ttl_seconds=settings.cache_ttl_seconds
)
