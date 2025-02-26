"""
Tool API Schemas

This module defines the request and response schemas for the tools API:
- Request schemas for creating and updating tools
- Response schemas for different view types (detail, brief, list)
- Validation rules and field constraints
- Example data for API documentation

The schemas use Pydantic for validation and serialization, ensuring
type safety and consistent API responses.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
from datetime import datetime

# Validation imports
from pydantic import BaseModel

from .tool import Tool, ToolUpdate,ToolProjection
from ..response_base import PaginatedResponse
from .examples import (
    TOOL_EXAMPLE, TOOL_UPDATE_EXAMPLE, TOOL_BRIEF_EXAMPLE, TOOL_LIST_EXAMPLE, TOOL_DETAIL_EXAMPLE
)

#-----------------------------------------------------------------------------
# Request Schemas
#-----------------------------------------------------------------------------

class CreateToolRequest(Tool):
    """Schema for tool creation endpoint."""
    model_config = {
        "json_schema_extra": {"example": TOOL_EXAMPLE}
    }

class UpdateToolRequest(ToolUpdate):
    """Schema for tool update endpoint."""
    model_config = {
        "json_schema_extra": {"example": TOOL_UPDATE_EXAMPLE}
    }

class DeleteToolRequest(BaseModel):
    """Schema for tool deletion endpoint."""
    id: str

class ToolDetailResponse(Tool):
    """Schema for detailed tool information."""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {"example": TOOL_DETAIL_EXAMPLE}
    }

class ToolBriefResponse(ToolProjection):
    """Schema for summarized tool information."""
    model_config = {
        "json_schema_extra": {"example": TOOL_BRIEF_EXAMPLE}
    }

class ToolListResponse(PaginatedResponse[ToolBriefResponse]):
    """Schema for paginated tool listings."""
    model_config = {
        "json_schema_extra": {"example": TOOL_LIST_EXAMPLE}
    }

