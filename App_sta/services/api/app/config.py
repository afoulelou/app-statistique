from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_version: str = "0.1.0"
    database_url: str = "postgresql+psycopg://app:app@localhost:5432/app_statistique"
    jwt_secret_key: str = "development-only-secret-change-me"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    dataset_storage_path: str = "storage/uploads"
    dataset_max_bytes: int = 10 * 1024 * 1024
    dataset_max_rows: int = 100_000

    @field_validator("database_url", mode="before")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
