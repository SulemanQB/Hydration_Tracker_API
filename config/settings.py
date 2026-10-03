import secrets
import logging
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Set up logger
logger = logging.getLogger("hydration_tracker.config")

class Settings(BaseSettings):
    """Environment-backed application settings with safe local defaults."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # MongoDB Configuration
    MONGODB_URI: str = Field(default="mongodb://localhost:27017")
    DB_NAME: str = Field(default="hydration_tracker")

    # API Configuration
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_DEBUG: bool = Field(default=False)
    API_BASE_URL: str = Field(default="http://localhost:8000")

    # Security settings
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    SECURE_COOKIES: bool = Field(default=False)

    # Logging
    LOG_LEVEL: str = Field(default="INFO")

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)

    # SSL/TLS is optional. Defaults serve HTTP.
    # Point SSL_CERT_PATH and SSL_KEY_PATH at local or mounted files via the
    # environment. Do not commit certificate or private key files.
    SSL_ENABLED: bool = Field(default=False, alias="SSL_ENABLED")
    SSL_CERT_PATH: Optional[str] = Field(default=None, alias="SSL_CERT_PATH")
    SSL_KEY_PATH: Optional[str] = Field(default=None, alias="SSL_KEY_PATH")

    @field_validator("MONGODB_URI")
    @classmethod
    def validate_mongodb_uri(cls, v):
        """Ensure MongoDB URI has proper protocol prefix"""
        if v and not v.startswith(("mongodb://", "mongodb+srv://")):
            return f"mongodb://{v}"
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """Ensure LOG_LEVEL is a valid Python logging level"""
        valid_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if v.upper() not in valid_levels:
            logger.warning(f"Invalid LOG_LEVEL: {v}. Using INFO instead.")
            return "INFO"
        return v.upper()

    @field_validator("RATE_LIMIT_PER_MINUTE")
    @classmethod
    def validate_rate_limit(cls, v):
        """Prevent an enabled limiter from accepting an unusable limit."""
        if v < 1:
            raise ValueError("RATE_LIMIT_PER_MINUTE must be at least 1")
        return v

# Create settings instance
settings = Settings()

# For backward compatibility
MONGODB_URI = settings.MONGODB_URI
DB_NAME = settings.DB_NAME
API_HOST = settings.API_HOST
API_PORT = settings.API_PORT
API_DEBUG = settings.API_DEBUG
SECRET_KEY = settings.SECRET_KEY
SECURE_COOKIES = settings.SECURE_COOKIES
LOG_LEVEL = settings.LOG_LEVEL
RATE_LIMIT_ENABLED = settings.RATE_LIMIT_ENABLED
RATE_LIMIT_PER_MINUTE = settings.RATE_LIMIT_PER_MINUTE
SSL_ENABLED = settings.SSL_ENABLED
SSL_CERT_PATH = settings.SSL_CERT_PATH
SSL_KEY_PATH = settings.SSL_KEY_PATH

# Display config (excluding sensitive data)
logger.info(f"Loaded configuration: DB_NAME={DB_NAME}, API_PORT={API_PORT}, LOG_LEVEL={LOG_LEVEL}")