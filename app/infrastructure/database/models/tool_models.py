"""
Tool Database Model

This module defines the MongoDB document structure for tools.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
from typing import Optional, List
from datetime import datetime

# Third-party imports
from pydantic import Field
from pymongo import IndexModel, TEXT
from beanie import Document

# Schemas imports
from ....schemas import (
    BestPractice, TroubleshootingItem, ImplementationGuide
)


# Constants for validation
MAX_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 300
MAX_OVERVIEW_LENGTH = 5000
ALLOWED_HTML_TAGS = ['p', 'h1', 'h2', 'h3', 'ul', 'li', 'code', 'pre']
ALLOWED_HTML_ATTRS = {'*': ['class']}

#-----------------------------------------------------------------------------
# Model Definition
#-----------------------------------------------------------------------------


class Tool(Document):
    """MongoDB document model for developer tools and technologies."""

    model_config = {
        "extra": "allow",
        "json_encoders": {datetime: str}
    }

    #-------------------------------------------------------------------------
    # Basic Information Fields
    #-------------------------------------------------------------------------

    name: str = Field(
        ...,
        description="Name of the tool",
        max_length=MAX_NAME_LENGTH,
        examples=["Docker", "Kubernetes", "Terraform"]
    )
    slug: Optional[str] = Field(
        None,
        description="URL-friendly version of name",
        examples=["docker", "kubernetes", "terraform"]
    )
    description: str = Field(
        ...,
        description="Short description",
        max_length=MAX_DESCRIPTION_LENGTH,
        examples=["Containerization platform", "Container orchestration system"]
    )
    image: Optional[str] = Field(
        None,
        description="Image URL",
        examples=["https://example.com/docker.png"]
    )

    #-------------------------------------------------------------------------
    # Detailed Content Fields
    #-------------------------------------------------------------------------

    overview: str = Field(
        ...,
        description="Detailed overview",
        max_length=MAX_OVERVIEW_LENGTH
    )
    tagline: str = Field(
        ...,
        description="Short tagline for tool",
    )
    category: str = Field(
        ...,
        description="Category of tool",
    )
    troubleshooting: List[TroubleshootingItem] = Field(
        default_factory=list,
        description="List of troubleshooting steps"
    )
    best_practices: List[BestPractice] = Field(
        default_factory=list,
        description="List of best practices"
    )
    implementations: List[ImplementationGuide] = Field(
        default_factory=list,
        description="List of implementation guides"
    )

    #-------------------------------------------------------------------------
    # Search and Classification Fields
    #-------------------------------------------------------------------------

    tags: List[str] = Field(
        default_factory=list,
        description="Searchable tags for categorization",
        examples=[["container", "devops", "microservices"]]
    )

    #-------------------------------------------------------------------------
    # Metadata Fields
    #-------------------------------------------------------------------------

    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of tool creation"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of last update"
    )


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
                [("name", TEXT), ("overview", TEXT), ("implementations", TEXT)],
                weights={"name": 10, "overview": 5, "implementations": 3}
            )
        ]
