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
from pydantic import Field, field_validator
from pymongo import IndexModel, TEXT
from slugify import slugify
import bleach

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
    """MongoDB document model for developer tools and technologies.
    
    Attributes:
        name: The name of the tool (required)
        slug: URL-friendly version of name (auto-generated)
        description: Brief description of the tool (required)
        image: URL to tool's image
        overview: Detailed explanation of the tool
        troubleshooting: List of common issues and solutions
        best_practices: List of recommended practices
        implementation: Technical implementation details
        tags: List of searchable keywords
        created_at: Timestamp of creation (auto-set)
        updated_at: Timestamp of last update (auto-set)
    """

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

    overview: Optional[str] = Field(
        None,
        description="Detailed overview",
        max_length=MAX_OVERVIEW_LENGTH
    )
    troubleshooting: List[str] = Field(
        default_factory=list,
        description="Common troubleshooting steps",
        examples=[["Check container logs", "Verify port mappings"]]
    )
    best_practices: List[str] = Field(
        default_factory=list,
        description="Recommended practices and tips",
        examples=[["Use multi-stage builds", "Implement health checks"]]
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
        description="Searchable tags for categorization",
        examples=[["container", "devops", "microservices"]]
    )

    @field_validator('overview', 'implementation')
    @classmethod
    def sanitize_html(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize HTML content to prevent XSS attacks."""
        if not v:
            return v
        return bleach.clean(
            v,
            tags=ALLOWED_HTML_TAGS,
            attributes=ALLOWED_HTML_ATTRS,
            strip=True
        )

    @field_validator('tags')
    @classmethod
    def normalize_tags(cls, v: List[str]) -> List[str]:
        """Normalize tags to lowercase and remove duplicates."""
        if not v:
            return []
        return list(set(tag.lower().strip() for tag in v if tag))

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
