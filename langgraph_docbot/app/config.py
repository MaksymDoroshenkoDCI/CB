import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    DOCS_OUTPUT_DIR: str = os.getenv("DOCS_OUTPUT_DIR", "generated_docs")
    MEMORY_FILE: str = os.getenv("MEMORY_FILE", "memory/session_memory.json")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    TEMPERATURE: float = 0.2

    class Config:
        env_file = ".env"


settings = Settings()

