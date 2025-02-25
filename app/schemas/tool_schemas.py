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
from typing import Optional, List
from datetime import datetime

# Validation imports
from pydantic import BaseModel, Field

from .troubleshooting_schemas import TroubleshootingItem
from .implementation_schema import ImplementationGuide
from .best_practice_schema import BestPractice

#-----------------------------------------------------------------------------
# Request Schemas
#-----------------------------------------------------------------------------

class CreateToolRequest(BaseModel):
    """Schema for tool creation endpoint.
    
    Validates and structures the data required to create a new tool.
    All fields are validated according to their types and constraints.
    """
    name: str
    slug: Optional[str]
    description: str
    image: Optional[str] = None
    overview: str
    tagline: str
    category: str
    troubleshooting: List[TroubleshootingItem]
    best_practices: List[BestPractice]
    implementations: List[ImplementationGuide]
    tags: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Docker",
                "slug": "docker",
                "description": "Containerization platform",
                "image": "https://example.com/docker.png",
                "overview": "Docker is a platform for developing, shipping, and running applications in containers.",
                "troubleshooting": [
                    {
                        "id": "1",
                        "title": "Container not starting",
                        "description": "The container fails to start due to a configuration issue.",
                        "solution": "Check the container logs using 'docker logs <container_id>'."
                    }
                ],
                "best_practices": [
                    {
                        "id": "1",
                        "title": "Use multi-stage builds",
                        "description": "Reduce image size and improve build efficiency."
                    }
                ],
                "implementations": [
                    {
                        "id": "1",
                        "title": "Setting up a basic Docker container",
                        "description": "Steps to create a simple container.",
                        "steps": [
                            "Install Docker.",
                            "Create a Dockerfile.",
                            "Build the image.",
                            "Run the container."
                        ]
                    }
                ],
                "tagline": "Empowering developers with containerization.",
                "category": "Containerization",
                "created_at": "2025-02-17T10:00:00Z",
                "updated_at": "2025-02-17T11:00:00Z"
            }
        }

class UpdateToolRequest(BaseModel):
    """Schema for tool update endpoint.
    
    All fields are optional since updates can be partial.
    Each present field will be validated according to its type.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    slug: Optional[str] = None
    overview: Optional[str] = None
    tagline: Optional[str] = None
    category: Optional[str] = None
    troubleshooting: Optional[List[TroubleshootingItem]] = None
    best_practices: Optional[List[BestPractice]] = None
    implementations: Optional[List[ImplementationGuide]] = None
    tags: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated description",
                "best_practices": ["New best practice"]
            }
        }

class DeleteToolRequest(BaseModel):
    """Schema for tool deletion endpoint."""
    id: str



#-----------------------------------------------------------------------------
# Response Schemas
#-----------------------------------------------------------------------------

class ToolDetailResponse(BaseModel):
    """Schema for detailed tool information.
    
    Used when returning complete information about a single tool.
    Includes all available fields and metadata.
    """
    id: str
    name: str
    description: str
    slug: str
    image: str
    overview: Optional[str]
    troubleshooting: List[TroubleshootingItem]
    best_practices: List[BestPractice]
    implementations: List[ImplementationGuide]
    tagline: Optional[str]
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Docker",
                "description": "Containerization platform",
                "image": "https://example.com/docker.png",
                "overview": "Detailed overview...",
                "troubleshooting": ["Check logs"],
                "best_practices": ["Use multi-stage builds"],
                "implementation": "Implementation guide...",
                "created_at": "2025-02-17T10:00:00Z",
                "updated_at": "2025-02-17T11:00:00Z"
            }
        }

class ToolBriefResponse(BaseModel):
    """Schema for summarized tool information.
    
    Used in list views where complete details aren't necessary.
    Contains only essential fields for tool identification.
    """
    id: str
    name: str
    image: str
    description: str
    slug: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Docker",
                "image": "https://example.com/docker.png",
                "description": "Containerization platform",
                "slug": "docker"
            }
        }

class ToolListResponse(BaseModel):
    """Schema for paginated tool listings.
    
    Combines a list of brief tool responses with pagination metadata.
    Used for endpoints that return multiple tools.
    
    Attributes:
        items: List of tools in brief format
        total: Total number of tools available
        skip: Number of tools skipped (offset)
        limit: Maximum number of tools per page
    """
    items: List[ToolBriefResponse]
    total: int
    skip: int
    limit: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "name": "Docker",
                        "image": "https://example.com/docker.png",
                        "description": "Containerization platform",
                        "slug": "docker"
                    }
                ],
                "total": 100,
                "skip": 0,
                "limit": 10
            }
        }


#-----------------------------------------------------------------------------
# State Schemas
#-----------------------------------------------------------------------------
class ReviewAction(BaseModel):
    task: str  # "approve" or "approve_with_updates"
    details: Optional[str]  # "Add more best practices for security"
    status: str = "pending"  # "pending", "processed"
    processed_at: Optional[datetime] = None

class ToolState(BaseModel):
    """Strict schema for LangGraph AI Workflow"""
    tool_id: str = Field(..., description="Unique Tool ID")
    name: str = Field(..., description="Tool Name")
    description: str = Field(..., description="Tool Description")
    image: Optional[str] = None
    overview: str
    tagline: str
    category: str
    troubleshooting: List[TroubleshootingItem] = []
    best_practices: List[BestPractice] = []
    status: str = "needs_review"  # needs_review → needs_processing → approved
    review_actions: List[ReviewAction] = []
    updated_at: datetime = Field(default_factory=datetime.now)