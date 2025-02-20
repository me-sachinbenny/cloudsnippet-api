from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """MongoDB settings"""
    MONGO_URI: str
    DB_NAME: str

    class Config:
        env_file = ".env"

