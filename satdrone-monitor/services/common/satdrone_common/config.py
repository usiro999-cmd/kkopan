from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SATDRONE_",
        extra="ignore",
    )

    environment: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://satdrone:satdrone@postgres:5432/satdrone"
    redis_url: str = "redis://redis:6379/0"
    rabbitmq_url: str = "amqp://satdrone:satdrone@rabbitmq:5672/"


@lru_cache
def get_settings() -> Settings:
    return Settings()

