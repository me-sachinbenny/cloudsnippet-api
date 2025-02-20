from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from ...models.tool_models import Tool
from ...core.config.settings import Settings


@lru_cache()
def get_settings() -> Settings:
    """Get MongoDB settings from environment"""
    return Settings()

async def get_db():
    """Get MongoDB database connection
    
    This is the main dependency you should use in your FastAPI endpoints.
    Example:
        @router.get("/")
        async def my_endpoint(db = Depends(get_db)):
            # Use db here
    """
    settings = get_settings()
    
    # Create client and connect to database
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.DB_NAME]
    
    try:
        # Initialize beanie ODM
        await init_beanie(database=db, document_models=[Tool])
        yield db
    finally:
        client.close()

async def close_mongodb_connection() -> None:
    """Close MongoDB connection"""
    global _mongodb_client
    if _mongodb_client is not None:
        _mongodb_client.close()
        _mongodb_client = None
