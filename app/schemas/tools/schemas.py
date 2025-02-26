"""Request and response schemas for tools."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from ..response_base import PaginatedResponse
from .base import Tool, ToolProjection

class CreateToolRequest(Tool):
    """Schema for tool creation endpoint."""

class UpdateToolRequest(Tool):
    """Schema for tool update endpoint."""

class DeleteToolRequest(BaseModel):
    """Schema for tool deletion endpoint."""
    id: str

class ToolDetailResponse(Tool):
    """Schema for detailed tool information."""
    id: str
    created_at: datetime
    updated_at: datetime

class ToolBriefResponse(ToolProjection):
    """Schema for summarized tool information."""

class ToolListResponse(PaginatedResponse[ToolBriefResponse]):
    """Schema for paginated tool listings."""
