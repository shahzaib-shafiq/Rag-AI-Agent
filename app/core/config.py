from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Product API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    ollama_base_url: str = "http://localhost:11434"
    ollama_embed_model: str = "nomic-embed-text"
    ollama_chat_model: str = "llama3.2:1b"
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection: str = "documents"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    rag_top_k: int = 6
    rag_max_distance: float = 0.5
    rag_max_query_length: int = 1000

    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/rag_ai"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
