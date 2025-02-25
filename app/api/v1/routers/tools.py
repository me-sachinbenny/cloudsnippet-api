"""Tools Router

This module handles all tool-related HTTP endpoints including:
- Create, Read, Update, Delete (CRUD) operations
- List all tools with pagination
- Get tool by ID or slug
- Search tools by text or tags

All endpoints use MongoDB for persistence and follow REST conventions.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# FastAPI imports
from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional

import re  

# Application imports
from ....schemas.tool_schemas import (
    CreateToolRequest, UpdateToolRequest,DeleteToolRequest,
    ToolDetailResponse, ToolBriefResponse,
    ToolListResponse
)

from ....services.tool_service import ToolService
from ....infrastructure.database.mongodb import get_db

#-----------------------------------------------------------------------------
# Dependencies
#-----------------------------------------------------------------------------

def get_tool_service(db = Depends(get_db)) -> ToolService:
    """Dependency injection for ToolService.
    
    Args:
        db: MongoDB database from dependency injection
        
    Returns:
        ToolService: Initialized tool service with database
    """
    return ToolService(db)

#-----------------------------------------------------------------------------
# Router Configuration
#-----------------------------------------------------------------------------

router = APIRouter(
    prefix="/tools",
    tags=["tools"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Resource not found"},
        status.HTTP_409_CONFLICT: {"description": "Resource already exists"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"}
    }
)

#-----------------------------------------------------------------------------
# Create Operations
#-----------------------------------------------------------------------------

@router.post(
    "/",
    response_model=ToolDetailResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tool",
    description="Create a new tool with the provided data. Name must be unique."
)
async def create_tool(
    tool_data: CreateToolRequest,   
    service: ToolService = Depends(get_tool_service)
) -> ToolDetailResponse:
    """Create a new tool in the system."""
    return await service.create(tool_data)

@router.post(
    "/generate-components",
    response_model=List[ToolDetailResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate tool components from a query",
    description="Extract tool names from input and create/update tool components using AI."
)
async def generate_components(
    query: str,
    service: ToolService = Depends(get_tool_service)
) -> List[ToolDetailResponse]:
    """Generate tool components from a query."""
    return await service.generate_components(query)


  

#-----------------------------------------------------------------------------
# Read Operations
#-----------------------------------------------------------------------------

@router.get(
    "/",
    response_model=ToolListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all tools",
    description="List all tools in the system with pagination support."
)
async def list_tools(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    service: ToolService = Depends(get_tool_service)
) -> ToolListResponse:
    """List all tools in the system with pagination support."""
    return await service.list_all(skip=skip, limit=limit)

@router.get(
    "/search",
    response_model=List[ToolBriefResponse],
    status_code=status.HTTP_200_OK,
    summary="Search tools",
    description="Search tools by text query or tag."
)
async def search_tools(
    q: Optional[str] = Query(None, description="Text to search in name, overview, and implementation"),
    tag: Optional[str] = Query(None, description="Tag to filter by"),
    service: ToolService = Depends(get_tool_service)
) -> List[ToolBriefResponse]:
    """Search tools by text or tag."""
    if tag:
        return await service.find_by_tag(tag)
    elif q:
        return await service.search(q)
    else:
        tools = await service.list_all()
        return tools.items

@router.get(
    "/{tool_id}",
    response_model=ToolDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get tool by ID",
    description="Get a specific tool by its unique identifier."
)
async def get_tool(
    tool_id: str,
    service: ToolService = Depends(get_tool_service)
) -> ToolDetailResponse:
    """Get a specific tool by ID."""
    return await service.get_by_id(tool_id)

@router.get(
    "/by-slug/{slug}",
    response_model=ToolDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get tool by slug",
    description="Get a specific tool by its URL-friendly slug."
)
async def get_tool_by_slug(
    slug: str,
    service: ToolService = Depends(get_tool_service)
) -> ToolDetailResponse:
    """Get a specific tool by slug."""
    return await service.get_by_slug(slug)

#-----------------------------------------------------------------------------
# Update Operations
#-----------------------------------------------------------------------------

@router.patch(
    "/{tool_id}",
    response_model=ToolDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update tool",
    description="Update an existing tool with the provided data."
)
async def update_tool(
    tool_id: str,
    tool_data: UpdateToolRequest,
    service: ToolService = Depends(get_tool_service)
) -> ToolDetailResponse:
    """Update an existing tool."""
    return await service.update(tool_id, tool_data)

#-----------------------------------------------------------------------------
# Delete Operations
#-----------------------------------------------------------------------------

@router.delete(
    "/{tool_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete tool",
    description="Delete a tool from the system."
)
async def delete_tool(
    tool_data: DeleteToolRequest,
    service: ToolService = Depends(get_tool_service)
) -> None:
    """Delete a tool from the system."""
    await service.delete(tool_data.id)

