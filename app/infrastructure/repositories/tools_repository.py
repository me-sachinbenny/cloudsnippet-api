"""
Tools Repository Layer

This module implements the data access layer for tool operations including:
- CRUD operations using Beanie ODM
- MongoDB query operations
- Error handling for database operations
- Pagination and projection support

The repository layer is responsible for all database interactions and
should be the only layer that directly works with the database models.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
from typing import List, Optional

# Framework imports
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

# Application imports
from ...models.tool_models import Tool


#-----------------------------------------------------------------------------
# Repository Implementation
#-----------------------------------------------------------------------------

class ToolsRepository:
    """Repository for handling tool-related database operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initializes repository with database connection."""
        self._db = db

    #-------------------------------------------------------------------------
    # Create Operations
    #-------------------------------------------------------------------------
    
    async def create(self, tool_data: dict) -> Tool:
        """Creates a new tool document in MongoDB."""
        try:
            tool = Tool(**tool_data)
            await tool.insert()
            return tool
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tool with name '{tool.name}' already exists"
            )

    #-------------------------------------------------------------------------
    # Read Operations (Direct Lookups)
    #-------------------------------------------------------------------------
    
    async def get_by_id(self, tool_id: str) -> Optional[Tool]:
        """Retrieves a tool document by its unique identifier."""
        tool = await Tool.get(tool_id)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool with id '{tool_id}' not found"
            )
        return tool
    
    async def get_by_slug(self, slug: str) -> Optional[Tool]:
        """Retrieves a tool document by its URL-friendly slug."""
        tool = await Tool.find_one(Tool.slug == slug)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool with slug '{slug}' not found"
            )
        return tool

    #-------------------------------------------------------------------------
    # List Operations (Pagination)
    #-------------------------------------------------------------------------
    
    async def list_all(self, skip: int = 0, limit: int = 10) -> tuple[List[dict], int]:
        """Retrieves a paginated list of tools with essential fields only."""
        projection = {
            "_id": 1,      # Required for document identification
            "name": 1,    # Basic tool information
            "description": 1,
            "slug": 1,    # URL-friendly identifier
            "image": 1    # Tool icon or preview image
        }
        tools = await Tool.find_all().skip(skip).limit(limit).project(projection).to_list()
        total = await Tool.count()
        return tools, total

    #-------------------------------------------------------------------------
    # Update Operations
    #-------------------------------------------------------------------------
    
    async def update(self, tool_id: str, tool_data: dict) -> Tool:
        """Updates an existing tool document with new data."""
        tool = await self.get_by_id(tool_id)
        try:
            await tool.set(tool_data)
            return tool
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tool with name '{tool_data.get('name')}' already exists"
            )

    #-------------------------------------------------------------------------
    # Delete Operations
    #-------------------------------------------------------------------------
    
    async def delete(self, tool_id: str) -> None:
        """Removes a tool document from the database."""
        tool = await self.get_by_id(tool_id)
        await tool.delete()

    #-------------------------------------------------------------------------
    # Search and Filter Operations
    #-------------------------------------------------------------------------
    
    async def search(self, query: str) -> List[Tool]:
        """Performs full-text search across tool documents."""
        return await Tool.text_search(query)
    
    async def find_by_tag(self, tag: str) -> List[Tool]:
        """Filters tool documents by tag field."""
        return await Tool.find_by_tag(tag)
