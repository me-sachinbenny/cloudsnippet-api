"""
Tools Repository Layer

This module implements the data access layer for tool operations.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
from typing import List, Optional, Tuple
from bson import ObjectId

# Framework imports
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas import ToolDetailResponse

# Exception handling
from ...exceptions import EntityNotFoundException

from ...exceptions import RepositoryErrorHandler

# Application imports
from ..database.models import Tool

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
    
    @RepositoryErrorHandler.handle_operation
    async def create(self, tool_data: dict) -> Tool:
        """Creates a new tool document."""
        tool = Tool(**tool_data)
        await tool.insert()
        return tool
    
    @RepositoryErrorHandler.handle_operation
    async def create_many(self, tools_data: List[dict]) -> List[Tool]:
        """Creates multiple tool documents."""
        tools = []
        for tool_data in tools_data:
            tool = Tool(**tool_data)
            await tool.insert()
            tools.append(tool)
        return tools

    @RepositoryErrorHandler.handle_operation
    async def _create_field(self, item:dict,tool_id: str) -> ToolDetailResponse:
        tool = await self.get_by_id(tool_id)
        tool[item["field_name"]] = item["field_data"]
        await tool.save()
        return tool
    
    #-------------------------------------------------------------------------
    # Read Operations (Direct Lookups)
    #-------------------------------------------------------------------------
    
    @RepositoryErrorHandler.handle_operation
    async def get_by_id(self, tool_id: str) -> Optional[Tool]:
        """Retrieves a tool document."""
        object_id = ObjectId(tool_id)
        tool = await Tool.find_one({"_id": object_id})
        if not tool:
            raise EntityNotFoundException("Tool", "id", tool_id)
        return tool
    
    @RepositoryErrorHandler.handle_operation
    async def get_by_slug(self, slug: str) -> Optional[Tool]:
        """Retrieves a tool document."""
        tool = await Tool.find_one(Tool.slug == slug)
        if not tool:
            raise EntityNotFoundException("Tool", "slug", slug)
        return tool

    #-------------------------------------------------------------------------
    # List Operations (Pagination)
    #-------------------------------------------------------------------------
    
    async def list_all(self, skip: int = 0, limit: int = 10) -> Tuple[List[Tool], int]:
        tools = await Tool.find_all().skip(skip).limit(limit).to_list()
        total = await Tool.count()
        return tools, total

    #-------------------------------------------------------------------------
    # Update Operations
    #-------------------------------------------------------------------------
    
    @RepositoryErrorHandler.handle_operation
    async def update(self, tool_id: str, tool_data: dict) -> Tool:
        """Updates an existing tool document."""
        tool = await self.get_by_id(tool_id)
        await tool.set(tool_data)
        return tool
 
    
    @RepositoryErrorHandler.handle_operation
    async def update_many(self, tools_data: List[dict]) -> List[Tool]:
        """Updates multiple tool documents."""
        tools = []
        for tool_data in tools_data:
            tool = await self.get_by_id(tool_data.get("id"))
            await tool.set(tool_data)
            tools.append(tool)
        return tools
    
    @RepositoryErrorHandler.handle_operation
    async def update_field(self, tool_id: str, field_name: str, field_data: dict) -> Tool:
        """Updates a specific field of a tool document."""
        tool = await self.get_by_id(tool_id)
        await tool.set({field_name: field_data})
        return tool
    
    #-------------------------------------------------------------------------
    # Delete Operations
    #-------------------------------------------------------------------------
    
    async def delete(self, tool_id: str) -> None:
        """Removes a tool document."""
        tool = await self.get_by_id(tool_id)
        await tool.delete()
    
  

    #-------------------------------------------------------------------------
    # Search and Filter Operations
    #-------------------------------------------------------------------------
    
    async def search(self, query: str) -> List[Tool]:
        """Performs full-text search."""
        return await Tool.text_search(query)
    
    async def find_by_tag(self, tag: str) -> List[Tool]:
        """Filters tool documents."""
        return await Tool.find_by_tag(tag)
