"""
Tool Database Model

This module defines the MongoDB document structure for tools including:
- Basic tool information (name, description, image)
- Detailed content (overview, troubleshooting, best practices)
- Search capabilities (tags, text search)
- Security features (HTML sanitization)
- Automatic field generation (slugs, timestamps)

The model uses Beanie ODM for MongoDB integration and includes
validation rules, text indexes, and example data for documentation.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
from typing import Optional, List
from datetime import datetime

# Third-party imports
from beanie import Document, before_event, Insert, Replace
from pydantic import Field
from pymongo import IndexModel, TEXT
from slugify import slugify
import bleach

#-----------------------------------------------------------------------------
# Model Definition
#-----------------------------------------------------------------------------

class Tool(Document):
    """MongoDB document model for developer tools and technologies."""

    #-------------------------------------------------------------------------
    # Basic Information Fields
    #-------------------------------------------------------------------------

    name: str = Field(
        ..., 
        description="Name of the tool",
        max_length=100
    )
    slug: Optional[str] = Field(
        None,
        description="URL-friendly version of name"
    )
    description: str = Field(
        ...,
        description="Short description",
        max_length=300
    )
    image: Optional[str] = Field(
        None,
        description="Image URL"
    )

    #-------------------------------------------------------------------------
    # Detailed Content Fields
    #-------------------------------------------------------------------------

    overview: Optional[str] = Field(
        None,
        description="Detailed overview"
    )
    troubleshooting: List[str] = Field(
        default_factory=list,
        description="Common troubleshooting steps"
    )
    best_practices: List[str] = Field(
        default_factory=list,
        description="Recommended practices and tips"
    )
    implementation: Optional[str] = Field(
        None,
        description="Technical details and implementation guide"
    )

    #-------------------------------------------------------------------------
    # Search and Classification Fields
    #-------------------------------------------------------------------------

    tags: List[str] = Field(
        default_factory=list,
        description="Searchable tags for categorization"
    )

    #-------------------------------------------------------------------------
    # Metadata Fields
    #-------------------------------------------------------------------------

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of tool creation"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of last update"
    )

    #-------------------------------------------------------------------------
    # Event Hooks
    #-------------------------------------------------------------------------

    @before_event([Insert])
    def set_slug(self) -> None:
        """Automatically generates URL-friendly slug from tool name."""
        if not self.slug:
            self.slug = slugify(self.name)

    @before_event([Insert, Replace])
    def sanitize_and_timestamp(self) -> None:
        """Updates timestamp and sanitizes HTML content for security."""
        self.updated_at = datetime.utcnow()
        if self.overview:
            self.overview = bleach.clean(self.overview)
        if self.implementation:
            self.implementation = bleach.clean(self.implementation)

    #-------------------------------------------------------------------------
    # Search Methods
    #-------------------------------------------------------------------------

    @classmethod
    async def find_by_tag(cls, tag: str) -> List["Tool"]:
        """Finds tools by tag for category-based filtering."""
        return await cls.find_many(Tool.tags == tag).to_list()

    @classmethod
    async def text_search(cls, query: str) -> List["Tool"]:
        """Performs full-text search across tool fields."""
        return await cls.find({"$text": {"$search": query}}).to_list()

    #-------------------------------------------------------------------------
    # Collection Configuration
    #-------------------------------------------------------------------------

    class Settings:
        """MongoDB collection settings with weighted text indexes."""
        name = "tools"
        indexes = [
            # Text index with field weights for relevance-based search
            IndexModel(
                [("name", TEXT), ("overview", TEXT), ("implementation", TEXT)],
                weights={"name": 10, "overview": 5, "implementation": 3}
            )
        ]

    class Config:
        """Model configuration with example data for API docs."""
        json_schema = {
            "example": {
                "name": "Docker",
                "slug": "docker",
                "description": "Containerization platform",
                "image": "https://example.com/docker-logo.svg",
                "overview": "Docker allows you to containerize applications...",
                "troubleshooting": ["Check logs", "Restart container"],
                "best_practices": ["Use small images", "Limit privileges"],
                "implementation": "docker run hello-world",
                "tags": ["containerization", "devops"]
            }
        }