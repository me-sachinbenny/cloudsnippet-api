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
from typing import List, Optional, Tuple
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator

# Framework imports
from motor.motor_asyncio import AsyncIOMotorDatabase

# Exception handling
from ..exceptions.repository_exceptions import (
    DuplicateEntityException,
    EntityNotFoundException,
    InvalidIdentifierException
)
from ..exceptions.error_handler import RepositoryErrorHandler

# Application imports
from ...models.tool_models import Tool
from ...schemas.best_practice_schema import BestPractice
from ...schemas.implementation_schema import ImplementationGuide
from ...schemas.troubleshooting_schemas import TroubleshootingItem



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
        """Creates a new tool document in MongoDB."""
        tool = Tool(**tool_data)
        await tool.insert()
        return tool
    
    @RepositoryErrorHandler.handle_operation
    async def create_many(self, tools_data: List[dict]) -> List[Tool]:
        """Creates multiple tool documents in MongoDB."""
        tools = []
        for tool_data in tools_data:
            tool = Tool(**tool_data)
            await tool.insert()
            tools.append(tool)
        return tools
    
    @RepositoryErrorHandler.handle_operation
    async def _create_best_practices(self, items: List[dict]) -> List[BestPractice]:
        for item in items:
            item["id"] = self._generate_id("bp", item)
            best_practice = BestPractice(**item)
            await best_practice.insert()
            return best_practice
    
    @RepositoryErrorHandler.handle_operation
    async def _create_troubleshooting_items(self, items: List[dict]) -> List[TroubleshootingItem]:
        for item in items:
            item["id"] = self._generate_id("tr", item)
            troubleshooting_item = TroubleshootingItem(**item)
            await troubleshooting_item.insert()
            return troubleshooting_item

    
    @RepositoryErrorHandler.handle_operation
    async def _create_root_causes(self, items: List[dict]) -> List[RootCause]:
        for item in items:
            item["id"] = self._generate_id("rc", item)
            root_cause = RootCause(**item)
            await root_cause.insert()
            return root_cause

    
    @RepositoryErrorHandler.handle_operation
    async def _create_solutions(self, items: List[dict]) -> List[Solution]:
        for item in items:
            item["id"] = self._generate_id("so", item)
            solution = Solution(**item)
            await solution.insert()
            return solution



    #-------------------------------------------------------------------------
    # Read Operations (Direct Lookups)
    #-------------------------------------------------------------------------
    
    @RepositoryErrorHandler.handle_operation
    async def get_by_id(self, tool_id: str) -> Optional[Tool]:
        """Retrieves a tool document by its unique identifier."""
        object_id = ObjectId(tool_id)
        tool = await Tool.find_one({"_id": object_id})
        if not tool:
            raise EntityNotFoundException("Tool", "id", tool_id)
        return tool
    
    @RepositoryErrorHandler.handle_operation
    async def get_by_slug(self, slug: str) -> Optional[Tool]:
        """Retrieves a tool document by its URL-friendly slug."""
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
        """Updates an existing tool document with new data."""
        tool = await self.get_by_id(tool_id)
        await tool.set(tool_data)
        return tool
 
    
    @RepositoryErrorHandler.handle_operation
    async def update_many(self, tools_data: List[dict]) -> List[Tool]:
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
