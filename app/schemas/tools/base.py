"""Base schemas for tools."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .troubleshooting import TroubleshootingItem
from .implementation import ImplementationGuide
from .best_practice import BestPractice

class ToolBase(BaseModel):
    """Common fields for tool schemas."""
    name: str
    description: str
    image: Optional[str] = None
    slug: Optional[str] = None

class Tool(ToolBase):
    """Base schema for a tool."""
    overview: str
    tagline: str
    category: str
    troubleshooting: List[TroubleshootingItem] = []
    best_practices: List[BestPractice] = []
    implementations: List[ImplementationGuide] = []
    tags: List[str] = []

class ToolUpdate(BaseModel):
    """Base schema for tool updates."""
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

class ToolProjection(ToolBase):
    """Projection schema for tool summaries."""
    id: str

    model_config = {
        "validate_assignment": True,
        "extra": "ignore"
    }

class ReviewAction(BaseModel):
    """Review action in the AI workflow."""
    task: str  # "approve" or "approve_with_updates"
    details: Optional[str]  # "Add more best practices for security"
    status: str = "pending"  # "pending", "processed"
    processed_at: Optional[datetime] = None

class ToolState(Tool):
    """Tool state in the AI workflow."""
    tool_id: str = Field(..., description="Unique Tool ID")
    status: str = "needs_review"  # needs_review → needs_processing → approved
    review_actions: List[ReviewAction] = []
    updated_at: datetime = Field(default_factory=datetime.now)
