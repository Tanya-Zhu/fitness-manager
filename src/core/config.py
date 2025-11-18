"""Application configuration management."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # Application
    app_env: str = "development"
    log_level: str = "INFO"

    # Database
    database_url: str

    # Redis (使用 memory:// 可以不依赖 Redis 服务)
    redis_url: str = "memory://"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"  # 使用对称加密算法
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["*"]  # 允许所有来源访问（局域网分享）

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100


settings = Settings()
