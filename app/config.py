from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = (
        "postgresql+psycopg2://mac@localhost:5433/customer_feedback"
    )
    app_name: str = "Customer Feedback Analyzer"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2:1b"
    ollama_timeout: float = 120.0
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


settings = Settings()
