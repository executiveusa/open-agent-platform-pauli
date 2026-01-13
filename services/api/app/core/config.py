import os
from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://oap:oap@postgres:5432/oap")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    api_token: str | None = os.getenv("API_TOKEN")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    temporal_enabled: bool = os.getenv("TEMPORAL_ENABLED", "true").lower() == "true"
    temporal_address: str = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
    temporal_namespace: str = os.getenv("TEMPORAL_NAMESPACE", "default")
    run_token_secret: str = os.getenv("RUN_TOKEN_SECRET", "change-me")
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
    langfuse_host: str | None = os.getenv("LANGFUSE_HOST")
    langfuse_public_key: str | None = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = os.getenv("LANGFUSE_SECRET_KEY")


@lru_cache

def get_settings() -> Settings:
    return Settings()
