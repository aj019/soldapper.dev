from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    HELIUS_API_KEY: str
    FETCH_AI_API_KEY: str
    OPENAI_API_KEY: str
    HELIUS_API_URL: str = "https://api.helius.xyz/v0"
    API_KEY: str  # For internal API authentication
    
    class Config:
        env_file = ".env"

settings = Settings() 