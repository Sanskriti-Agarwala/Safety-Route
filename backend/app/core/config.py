from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "SafetyNavigationAPI"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    DATABASE_URL: str = "sqlite:///./safety_nav.db"
    
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    HF_API_TOKEN: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()