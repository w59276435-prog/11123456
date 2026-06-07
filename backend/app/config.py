"""应用配置管理"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    app_name: str = "Personal Info Management System"
    app_version: str = "2.0.0"
    debug: bool = True
    
    # 数据库
    database_url: str = "sqlite:///./data.db"
    
    # 安全
    secret_key: str = "your-secret-key-change-in-production"
    pi_enc_key: str = "your-32-char-encryption-key-change-in-prod"
    
    # JWT
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    jwt_refresh_expire_days: int = 7
    
    # CORS
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # 文件上传
    max_upload_size_mb: int = 10
    allowed_upload_extensions: List[str] = ["jpg", "jpeg", "png", "bmp", "webp", "gif"]
    
    # 日志
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
