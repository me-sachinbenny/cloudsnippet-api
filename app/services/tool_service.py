"""
Tool Service Layer

This module implements the service layer for tool operations including:
- CRUD operations for tools
- Data transformation between API and database formats
- Business logic implementation
- Response preparation and validation
- Search and filtering functionality

The service layer acts as an intermediary between the API routes and the
database repository, ensuring proper data validation and transformation.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
from datetime import datetime
from typing import List, Dict, Any

# Framework imports
from motor.motor_asyncio import AsyncIOMotorDatabase

# Application imports
from ..schemas.tool_schemas import CreateToolRequest, UpdateToolRequest
from ..schemas.tool_schemas import ToolDetailResponse, ToolBriefResponse, ToolListResponse

from ..infrastructure.repositories.tools_repository import ToolsRepository

#-----------------------------------------------------------------------------
# Service Implementation
#-----------------------------------------------------------------------------

class ToolService:
    """Service layer for managing tool operations with business logic."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize service with database connection."""
        self.repository = ToolsRepository(db)

    #-------------------------------------------------------------------------
    # Helper Methods
    #-------------------------------------------------------------------------

    def _prepare_response(self, data: Any) -> Dict[str, Any]:
        """Transforms MongoDB document format to API response format.
        
        Handles both dictionary and Beanie Document inputs by converting them
        to a format suitable for Pydantic response models.
        """
        if hasattr(data, 'model_dump'):
            # If it's a Beanie Document or Pydantic model
            data_dict = data.model_dump()
            if hasattr(data, 'id'):
                data_dict['id'] = str(data.id)
            return data_dict
        elif isinstance(data, dict):
            # If it's already a dictionary
            if '_id' in data:
                data['id'] = str(data.pop('_id'))
            return data
        else:
            raise ValueError(f'Unsupported data type for response preparation: {type(data)}')

    #-------------------------------------------------------------------------
    # Create Operations
    #-------------------------------------------------------------------------

    async def create(self, data: CreateToolRequest) -> ToolDetailResponse:
        """Creates a new tool in the database and returns its details."""
        tool = await self.repository.create(data.model_dump())
        return ToolDetailResponse(**self._prepare_response(tool))

    #-------------------------------------------------------------------------
    # Read Operations (Direct Lookups)
    #-------------------------------------------------------------------------

    async def get_by_id(self, tool_id: str) -> ToolDetailResponse:
        """Get a specific tool by ID."""
        tool = await self.repository.get_by_id(tool_id)
        return ToolDetailResponse(**self._prepare_response(tool))
    
    async def get_by_slug(self, slug: str) -> ToolDetailResponse:
        """Retrieves a specific tool using its URL-friendly slug identifier."""
        tool = await self.repository.get_by_slug(slug)
        return ToolDetailResponse(**self._prepare_response(tool))

    #-------------------------------------------------------------------------
    # List Operations (Pagination)
    #-------------------------------------------------------------------------

    async def list_all(self, skip: int = 0, limit: int = 10) -> ToolListResponse:
        """Retrieves a paginated list of tools with total count and pagination metadata."""
        tools, total = await self.repository.list_all(skip, limit)
        return ToolListResponse(
            items=[ToolBriefResponse(**self._prepare_response(t)) for t in tools],
            total=total,
            skip=skip,
            limit=limit
        )

    #-------------------------------------------------------------------------
    # Update Operations
    #-------------------------------------------------------------------------

    async def update(self, tool_id: str, data: UpdateToolRequest) -> ToolDetailResponse:
        """Updates an existing tool with new data and updates the timestamp."""
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now()
        tool = await self.repository.update(tool_id, update_data)
        return ToolDetailResponse(**self._prepare_response(tool))

    #-------------------------------------------------------------------------
    # Delete Operations
    #-------------------------------------------------------------------------

    async def delete(self, tool_id: str) -> None:
        """Verifies tool existence and removes it from the database."""
        # First verify the tool exists
        await self.get_by_id(tool_id)
        # Then delete it through the repository
        await self.repository.delete(tool_id)

    #-------------------------------------------------------------------------
    # Search and Filter Operations
    #-------------------------------------------------------------------------
        
    async def search(self, query: str) -> List[ToolBriefResponse]:
        """Performs a text search across tool fields and returns matching tools."""
        tools = await self.repository.search(query)
        return [ToolBriefResponse(**self._prepare_response(t)) for t in tools]
    
    async def find_by_tag(self, tag: str) -> List[ToolBriefResponse]:
        """Filters and returns tools that have the specified tag."""
        tools = await self.repository.find_by_tag(tag)
        return [ToolBriefResponse(**self._prepare_response(t)) for t in tools]
        


