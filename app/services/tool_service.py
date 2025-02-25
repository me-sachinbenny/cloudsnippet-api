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

# Third-party imports
from motor.motor_asyncio import AsyncIOMotorDatabase

# Application imports
from ..models.tool_models import ToolState
from ..infrastructure.agents.data_generator import AI_Data_Generator

# Utility imports
from ..utlis.findTools import FindTools

# Framework imports
from motor.motor_asyncio import AsyncIOMotorDatabase

# Application imports
from ..schemas.tool_schemas import CreateToolRequest, UpdateToolRequest
from ..schemas.tool_schemas import ToolDetailResponse, ToolBriefResponse, ToolListResponse

from ..schemas.tool_projection import ToolProjection
from ..schemas.implementation_schema import ImplementationGuide

from ..infrastructure.repositories.tools_repository import ToolsRepository



#-----------------------------------------------------------------------------
# Service Implementation
#-----------------------------------------------------------------------------

class ToolService:
    """Service layer for managing tool operations with business logic."""

    def __init__(self, db: AsyncIOMotorDatabase , ):
        """Initialize service with database connection."""
        self.repository = ToolsRepository(db)
        self.generator = AI_Data_Generator(db, )
    
    def document_to_dict_with_str_id(self, document) -> dict:
        doc_dict = document.dict()
        doc_dict["id"] = str(document.id)
        # Ensure required fields have default values
        doc_dict["slug"] = doc_dict.get("slug", "") or ""
        doc_dict["image"] = doc_dict.get("image", "") or ""
        return doc_dict

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

    async def generate_components(self, query: str) -> List[ToolDetailResponse]:
        """Generate tool components from a natural language query."""
        # Extract tool names from the query using utility
        candidate_tool_names = FindTools.extract_tool_names(query)
        
        # Generate tool data for each candidate using AI
        tool_creation_requests: List[CreateToolRequest] = []
        for tool_name in candidate_tool_names:
            ai_generated_tool = await self.generator.initial_query(tool_name)
            tool_creation_requests.append(ai_generated_tool)

        # Bulk create tools in database
        created_tools = await self.repository.create_many([
            tool_request.model_dump() for tool_request in tool_creation_requests
        ])
        
        # Transform to response format
        return [ToolDetailResponse(**self._prepare_response(tool)) for tool in created_tools]


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
        tools_raw, total = await self.repository.list_all(skip, limit)
        tools = []
        for tool in tools_raw:
            tool_dict = self.document_to_dict_with_str_id(tool)
            tools.append(ToolProjection(**tool_dict))
        return ToolListResponse(
            items=[ToolBriefResponse(**self._prepare_response(t)) for t in tools],
            total=total,
            skip=skip,
            limit=limit)

    #-------------------------------------------------------------------------
    # AI Review Operations
    #-------------------------------------------------------------------------


        
    #-------------------------------------------------------------------------
    # Update Operations
    #-------------------------------------------------------------------------

    async def update(self, tool_id: str, data: UpdateToolRequest) -> ToolDetailResponse:
        """Updates an existing tool with new data and updates the timestamp."""
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now()
        tool = await self.repository.update(tool_id, update_data)
        return ToolDetailResponse(**self._prepare_response(tool))
    
    async def update_root_cause(self, tool_id: str, cause_data: dict) -> ToolDetailResponse:
        """Updates the root cause of a tool."""
        # Validate root cause data
        root_cause = RootCause(**cause_data)
        
        # Update the tool's root cause field
        updated_tool = await self.repository.update_field(tool_id, "root_cause", root_cause.dict())
        return ToolDetailResponse(**self._prepare_response(updated_tool))
    
    async def update_implementation_guide(self, tool_id: str, guide_data: dict) -> ToolDetailResponse:
        """Updates the implementation guide of a tool."""
        # Validate implementation guide data
        guide = ImplementationGuide(**guide_data)
        
        # Update the tool's implementation guide field
        updated_tool = await self.repository.update_field(tool_id, "implementation_guide", guide.dict())
        return ToolDetailResponse(**self._prepare_response(updated_tool))

    async def create_many(self, tools_data: List[dict]) -> List[ToolDetailResponse]:
        """Creates multiple tools with validation."""
        # Validate data using Pydantic model
        validated_tools = []
        for data in tools_data:
            data["created_at"] = data["updated_at"] = datetime.now()
            validated_tools.append(CreateToolRequest(**data).dict())
        
        # Create in repository
        created_tools = await self.repository.create_many(validated_tools)
        
        # Convert to response format
        return [ToolDetailResponse(**self._prepare_response(tool)) for tool in created_tools]

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
        


