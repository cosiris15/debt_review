"""
Application Configuration

Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Debt Review System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # DeepSeek API (OpenAI-compatible)
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Anthropic API (for intelligent parsing with Claude)
    ANTHROPIC_API_KEY: str = ""

    # Aliyun Dashscope API (for qwen-vl-ocr)
    DASHSCOPE_API_KEY: str = ""
    QWEN_OCR_MODEL: str = "qwen-vl-ocr-2025-11-20"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Clerk Authentication
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    OUTPUT_DIR: str = "./outputs"
    MAX_UPLOAD_SIZE_MB: int = 100

    # Task Processing
    TASK_TIMEOUT_MINUTES: int = 60
    MAX_CONCURRENT_TASKS: int = 3
    TASK_POLL_INTERVAL_SECONDS: int = 5

    # Knowledge Management
    USE_DYNAMIC_KNOWLEDGE: bool = True  # Enable dynamic knowledge loading from files
    KNOWLEDGE_CACHE_TTL_SECONDS: int = 60  # Cache TTL for hot-reload support

    # CORS (for frontend)
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://debt.parallm.tech",
        "https://debt-review.pages.dev",
        "https://debt-review.vercel.app"
    ]

    # LangSmith Configuration (for LangGraph Studio)
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_TRACING: bool = False
    LANGSMITH_PROJECT: str = "debt-review-dev"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Allow extra env vars


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience access
settings = get_settings()
