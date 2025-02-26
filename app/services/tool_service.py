"""
Tool Service Layer

This module implements the service layer for tool operations.
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
from ..schemas import (
    # Base schemas
    Tool, ToolUpdate, ToolProjection, ToolState,
    # Request schemas
    CreateToolRequest, UpdateToolRequest,
    # Response schemas
    ToolDetailResponse, ToolBriefResponse, ToolListResponse,
    # Component schemas
    TroubleshootingItem, ImplementationGuide, ImplementationStep,
    BestPractice, RootCause, Solution
)

# Utility imports
from ..utlis.findTools import FindTools

from ..infrastructure.repositories.tools_repository import ToolsRepository



#-----------------------------------------------------------------------------
# Service Implementation
#-----------------------------------------------------------------------------

class ToolService:
    """Service layer for managing tool operations."""

    def __init__(self, db: AsyncIOMotorDatabase , ):
        """Initialize service with database connection."""
        self.repository = ToolsRepository(db)
        # self.generator = AI_Data_Generator(db, )
    
    def document_to_dict_with_str_id(self, document) -> dict:
        """Transforms a document to a dictionary with string ID."""
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
        """Transforms document format to API response format."""
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
        """Creates a new tool."""
        tool = await self.repository.create(data.model_dump())
        return ToolDetailResponse(**self._prepare_response(tool))

    # async def generate_components(self, query: str) -> List[ToolDetailResponse]:
    #     """Generate tool components from a query."""
    #     # Extract tool names from the query using utility
    #     candidate_tool_names = FindTools.extract_tool_names(query)
        
    #     # Generate tool data for each candidate using AI
    #     tool_creation_requests: List[CreateToolRequest] = []
    #     for tool_name in candidate_tool_names:
    #         ai_generated_tool = await self.generator.initial_query(tool_name)
    #         tool_creation_requests.append(ai_generated_tool)

    #     # Bulk create tools in database
    #     created_tools = await self.repository.create_many([
    #         tool_request.model_dump() for tool_request in tool_creation_requests
    #     ])
        
    #     # Transform to response format
    #     return [ToolDetailResponse(**self._prepare_response(tool)) for tool in created_tools]
    
    async def create_many(self, tools_data: List[dict]) -> List[ToolDetailResponse]:
        """Creates multiple tools."""
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
    # Read Operations (Direct Lookups)
    #-------------------------------------------------------------------------

    async def get_by_id(self, tool_id: str) -> ToolDetailResponse:
        """Gets a tool by ID."""
        tool = await self.repository.get_by_id(tool_id)
        return ToolDetailResponse(**self._prepare_response(tool))
    
    async def get_by_slug(self, slug: str) -> ToolDetailResponse:
        """Retrieves a tool using its slug."""
        tool = await self.repository.get_by_slug(slug)
        return ToolDetailResponse(**self._prepare_response(tool))

    #-------------------------------------------------------------------------
    # List Operations (Pagination)
    #-------------------------------------------------------------------------

    async def list_all(self, skip: int = 0, limit: int = 10) -> ToolListResponse:
        """Retrieves a paginated list of tools."""
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
    # Update Operations
    #-------------------------------------------------------------------------

    async def update_tool(self, tool_id: str, data: UpdateToolRequest) -> ToolDetailResponse:
        """Updates an existing tool."""
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now()
        tool = await self.repository.update(tool_id, update_data)
        return ToolDetailResponse(**self._prepare_response(tool))
    
    async def update_tool_field(self, tool_id: str, fields_data: dict,field_name: str) -> ToolDetailResponse:
        """Updates a specific field of a tool."""
        field_mapping = {
            "root_cause" : RootCause,
            "solution" : Solution,
            "troubleshooting" : TroubleshootingItem,
            "best_practices" : BestPractice,
            "implementation_guides" : ImplementationGuide
        }
        field_type = field_mapping.get(field_name)
        if not field_type:
            raise ValueError(f"Invalid field name: {field_name}")
        fields_data = field_type.model_validate(fields_data)
        tool = await self.repository.update_field(tool_id, field_name, fields_data)
        return ToolDetailResponse(**self._prepare_response(tool))


    #-------------------------------------------------------------------------
    # Delete Operations
    #-------------------------------------------------------------------------

    async def delete(self, tool_id: str) -> None:
        """Removes a tool from the database."""
        # First verify the tool exists
        await self.get_by_id(tool_id)
        # Then delete it through the repository
        await self.repository.delete(tool_id)

    #-------------------------------------------------------------------------
    # Search and Filter Operations
    #-------------------------------------------------------------------------
        
    async def search(self, query: str) -> List[ToolBriefResponse]:
        """Performs a text search across tool fields."""
        tools = await self.repository.search(query)
        return [ToolBriefResponse(**self._prepare_response(t)) for t in tools]
    
    async def find_by_tag(self, tag: str) -> List[ToolBriefResponse]:
        """Filters tools by tag."""
        tools = await self.repository.find_by_tag(tag)
        return [ToolBriefResponse(**self._prepare_response(t)) for t in tools]
