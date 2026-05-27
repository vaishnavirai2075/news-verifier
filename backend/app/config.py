from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()  # ← add this

class Settings(BaseSettings):
    APP_NAME: str = "News Verifier API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    GROQ_API_KEY: str = ""        # ← add this

    DATABASE_URL: str = ""
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"   # ← add this
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()