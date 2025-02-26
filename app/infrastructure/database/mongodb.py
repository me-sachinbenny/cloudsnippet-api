"""MongoDB database connection handling."""

from functools import lru_cache
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from ..database.models import Tool
from ...core.config import Settings

# Global client instance
_mongodb_client: Optional[AsyncIOMotorClient] = None

@lru_cache()
def get_settings() -> Settings:
    """Get MongoDB settings from environment."""
    return Settings()

async def init_mongodb():
    """Initialize MongoDB connection."""
    global _mongodb_client
    
    if _mongodb_client is None:
        settings = get_settings()
        _mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
        db = _mongodb_client[settings.DB_NAME]
        await init_beanie(database=db, document_models=[Tool])

async def get_db():
    """Get MongoDB database connection."""
    global _mongodb_client
    
    if _mongodb_client is None:
        await init_mongodb()
    
    return _mongodb_client[get_settings().DB_NAME]

async def close_mongodb_connection() -> None:
    """Close MongoDB connection."""
    global _mongodb_client
    
    if _mongodb_client is not None:
        _mongodb_client.close()
        _mongodb_client = None
