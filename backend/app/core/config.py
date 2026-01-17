"""
Application Configuration
=========================

This module provides centralized configuration management for the Safety Route backend.
It loads environment variables, provides default values, and exposes settings
across the application.

Configuration Sources:
1. Environment variables (.env file)
2. Default values (for development)
3. Override values (for testing)

Usage:
    from app.core.config import settings
    
    print(settings.APP_NAME)
    api_key = settings.OPENAI_API_KEY

Benefits:
- Single source of truth for configuration
- Type-safe settings access
- Easy environment switching (dev/staging/prod)
- Secure credential management

Author: Safety Route Team
Date: January 2026
"""

import os
from typing import Optional
from pathlib import Path


try:
    from dotenv import load_dotenv
    
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
except ImportError:
    pass


class Settings:
    """
    Application settings and configuration.
    
    All configuration values are loaded from environment variables with
    sensible defaults for development environments.
    
    Attributes:
        APP_NAME: Application name for logging and display
        ENV: Environment (development/staging/production)
        DEBUG: Enable debug mode with detailed error messages
        HOST: Server host address
        PORT: Server port number
        CORS_ORIGINS: Allowed CORS origins for API access
        
        API Keys:
        OPENAI_API_KEY: OpenAI API key for AI features
        HF_API_TOKEN: Hugging Face API token for ML inference
        
        Database:
        DATABASE_URL: Database connection string (future use)
        
        Security:
        SECRET_KEY: Secret key for JWT/session signing
        
        Feature Flags:
        ENABLE_AI_FEATURES: Enable/disable AI-powered features
        ENABLE_MOCK_DATA: Use mock data instead of real APIs
    """
    
    APP_NAME: str = os.getenv("APP_NAME", "Safety Route Backend")
    
    ENV: str = os.getenv("ENV", "development")
    
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    PORT: int = int(os.getenv("PORT", "8000"))
    
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"
    )
    
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    HF_API_TOKEN: Optional[str] = os.getenv("HF_API_TOKEN")
    
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-change-in-production-12345"
    )
    
    ENABLE_AI_FEATURES: bool = os.getenv(
        "ENABLE_AI_FEATURES", "true"
    ).lower() in ("true", "1", "yes")
    
    ENABLE_MOCK_DATA: bool = os.getenv(
        "ENABLE_MOCK_DATA", "true"
    ).lower() in ("true", "1", "yes")
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    MAX_ROUTES_PER_REQUEST: int = int(os.getenv("MAX_ROUTES_PER_REQUEST", "5"))
    
    DEFAULT_SAFETY_THRESHOLD: float = float(
        os.getenv("DEFAULT_SAFETY_THRESHOLD", "50.0")
    )
    
    ROUTE_CACHE_TTL_SECONDS: int = int(
        os.getenv("ROUTE_CACHE_TTL_SECONDS", "300")
    )
    
    @classmethod
    def get_cors_origins_list(cls) -> list:
        """
        Parse CORS origins string into a list.
        
        Returns:
            List of allowed origin URLs
        
        Example:
            >>> Settings.get_cors_origins_list()
            ['http://localhost:3000', 'http://localhost:5173']
        """
        return [origin.strip() for origin in cls.CORS_ORIGINS.split(",")]
    
    @classmethod
    def is_production(cls) -> bool:
        """
        Check if running in production environment.
        
        Returns:
            True if ENV is 'production'
        """
        return cls.ENV.lower() == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """
        Check if running in development environment.
        
        Returns:
            True if ENV is 'development'
        """
        return cls.ENV.lower() == "development"
    
    @classmethod
    def validate_required_keys(cls) -> dict:
        """
        Validate that required API keys are configured.
        
        Returns:
            Dictionary with validation status for each key
        
        Example:
            >>> validation = Settings.validate_required_keys()
            >>> if not validation['openai']:
            ...     print("OpenAI API key missing")
        """
        return {
            "openai": cls.OPENAI_API_KEY is not None and len(cls.OPENAI_API_KEY) > 0,
            "huggingface": cls.HF_API_TOKEN is not None and len(cls.HF_API_TOKEN) > 0
        }
    
    @classmethod
    def get_summary(cls) -> dict:
        """
        Get a summary of current configuration.
        
        Returns:
            Dictionary with non-sensitive configuration values
        
        Example:
            >>> summary = Settings.get_summary()
            >>> print(summary['app_name'])
            'Safety Route Backend'
        """
        return {
            "app_name": cls.APP_NAME,
            "environment": cls.ENV,
            "debug": cls.DEBUG,
            "host": cls.HOST,
            "port": cls.PORT,
            "ai_features_enabled": cls.ENABLE_AI_FEATURES,
            "mock_data_enabled": cls.ENABLE_MOCK_DATA,
            "openai_configured": cls.OPENAI_API_KEY is not None,
            "hf_configured": cls.HF_API_TOKEN is not None
        }


settings = Settings()


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Returns:
        Settings instance with current configuration
    
    Usage:
        >>> from app.core.config import get_settings
        >>> config = get_settings()
        >>> print(config.APP_NAME)
    """
    return settings


if __name__ == "__main__":
    """
    Display current configuration when run directly.
    
    Run: python -m app.core.config
    """
    print("=" * 60)
    print("Safety Route Backend Configuration")
    print("=" * 60)
    
    summary = settings.get_summary()
    for key, value in summary.items():
        print(f"{key:.<30} {value}")
    
    print("\n" + "=" * 60)
    print("API Key Validation")
    print("=" * 60)
    
    validation = settings.validate_required_keys()
    for key, valid in validation.items():
        status = "✓ Configured" if valid else "✗ Missing"
        print(f"{key:.<30} {status}")
    
    print("\n" + "=" * 60)
    
    if not settings.is_production():
        print("\n⚠️  Running in development mode")
        print("Set ENV=production for production deployment")
    
    if settings.ENABLE_MOCK_DATA:
        print("\n💡 Mock data is enabled")
        print("Set ENABLE_MOCK_DATA=false to use real APIs")