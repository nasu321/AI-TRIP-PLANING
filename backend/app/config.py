"""
Application configuration using Pydantic Settings.
Reads from .env file or environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Agentic AI Travel Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-in-production"
    BACKEND_URL: str = "http://localhost:8505"
    FRONTEND_PORT: int = 8501
    BACKEND_PORT: int = 8505

    # LLM
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-pro"

    # Database
    DATABASE_TYPE: str = "sqlite"
    DATABASE_URL: str = "sqlite+aiosqlite:///./travel_platform.db"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "travel_db"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""

    # External APIs - Mock flags
    WEATHER_API_KEY: str = ""
    WEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    USE_MOCK_WEATHER: bool = True

    GOOGLE_PLACES_API_KEY: str = ""
    USE_MOCK_PLACES: bool = True

    AMADEUS_CLIENT_ID: str = ""
    AMADEUS_CLIENT_SECRET: str = ""
    USE_MOCK_FLIGHTS: bool = True

    CURRENCY_API_KEY: str = ""
    USE_MOCK_CURRENCY: bool = True

    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"
    USE_MOCK_WHATSAPP: bool = True

    # PDF
    REPORTS_DIR: str = "./reports"
    PDF_COMPANY_NAME: str = "AI Travel Co."
    PDF_SUPPORT_EMAIL: str = "support@aitravel.com"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def is_llm_configured(self) -> bool:
        """Check if LLM provider API key is present."""
        if self.LLM_PROVIDER == "gemini":
            return bool(self.GEMINI_API_KEY)
        elif self.LLM_PROVIDER == "openai":
            return bool(self.OPENAI_API_KEY)
        elif self.LLM_PROVIDER == "anthropic":
            return bool(self.ANTHROPIC_API_KEY)
        return False


# Singleton settings instance
settings = Settings()
