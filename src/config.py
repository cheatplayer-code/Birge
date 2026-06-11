"""
Application configuration using Pydantic Settings.
Reads from environment variables and .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    supabase_url: str = "https://your-project.supabase.co"
    supabase_anon_key: str = "your-anon-key-here"
    demo_mode: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode with synthetic data."""
        return self.demo_mode or not self.supabase_url.startswith("https://")


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings singleton."""
    return settings
