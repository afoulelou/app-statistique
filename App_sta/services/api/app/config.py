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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
