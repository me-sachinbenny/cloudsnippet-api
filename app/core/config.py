from pydantic_settings import BaseSettings
import logging

class Settings(BaseSettings):
    """Application settings"""
    # MongoDB settings
    MONGO_URI: str
    DB_NAME: str
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = True
    LOG_DIR: str = "logs"
    
    @property
    def log_level(self) -> int:
        """Convert string log level to logging module constant"""
        return getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)

    class Config:
        env_file = ".env"