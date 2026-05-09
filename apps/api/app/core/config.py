from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Production RAG Assistant"
    environment: str = "development"
    database_url: str
    redis_url: str
    qdrant_url: str
    ollama_base_url: str
    upload_dir: str = "/data/uploads"
    extraction_dir: str = "/data/extracted"
    max_upload_bytes: int = 10 * 1024 * 1024
    ai_base_url: str = "http://ollama:11434/v1"
    ai_api_key: str = "ollama"
    ai_embedding_model: str = "nomic-embed-text"
    ai_embedding_dimensions: int = 768
    qdrant_collection: str = "rag_chunks"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
