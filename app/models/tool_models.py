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
from pydantic import Field, field_validator,BaseModel
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

class RootCause(BaseModel):
    description: str
    factors: List[str]

class Solution(BaseModel):
    steps: List[str]
    prevention_tips: List[str]

class TroubleshootingItem(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    symptoms: List[str]
    root_cause: RootCause
    solution: Solution

class BestPractice(BaseModel):
    id: str
    title: str
    description: str

class ImplementationGuide(BaseModel):
    id: str
    title: str
    description: str
    steps: List[str]

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
        implementations: Technical implementation details
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

    # @field_validator('overview', 'implementations', check_fields=False)
    # @classmethod
    # def sanitize_html(cls, v: Optional[str]) -> Optional[str]:
    #     """Sanitize HTML content to prevent XSS attacks."""
    #     if not v:
    #         return v
    #     return bleach.clean(
    #         v,
    #         tags=ALLOWED_HTML_TAGS,
    #         attributes=ALLOWED_HTML_ATTRS,
    #         strip=True
    #     )

    # @field_validator('tags')
    # @classmethod
    # def normalize_tags(cls, v: List[str]) -> List[str]:
    #     """Normalize tags to lowercase and remove duplicates."""
    #     if not v:
    #         return []
    #     return list(set(tag.lower().strip() for tag in v if tag))

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

    # @before_event([Insert, Replace])
    # def pre_save_hook(self) -> None:
    #     """Pre-save hook for data validation and processing.
        
    #     Performs the following operations:
    #     1. Generates slug if not present
    #     2. Updates timestamps
    #     3. Sanitizes HTML content
    #     4. Normalizes tags
    #     5. Validates content lengths
    #     """
    #     # Generate slug if not present (only for new documents)
    #     if not self.slug:
    #         self.slug = slugify(self.name)

    #     # Update timestamps
    #     if not hasattr(self, 'created_at'):
    #         self.created_at = datetime.now()
    #     self.updated_at = datetime.now()

    #     # Sanitize HTML content
    #     if self.overview:
    #         self.overview = bleach.clean(
    #             self.overview,
    #             tags=ALLOWED_HTML_TAGS,
    #             attributes=ALLOWED_HTML_ATTRS,
    #             strip=True
    #         )

    #     # Sanitize troubleshooting items
    #     if self.troubleshooting:
    #         for item in self.troubleshooting:
    #             item.description = bleach.clean(
    #                 item.description,
    #                 tags=ALLOWED_HTML_TAGS,
    #                 attributes=ALLOWED_HTML_ATTRS,
    #                 strip=True
    #             )
    #             item.solution = bleach.clean(
    #                 item.solution,
    #                 tags=ALLOWED_HTML_TAGS,
    #                 attributes=ALLOWED_HTML_ATTRS,
    #                 strip=True
    #             )

    #     # Sanitize best practices
    #     if self.best_practices:
    #         for practice in self.best_practices:
    #             practice.description = bleach.clean(
    #                 practice.description,
    #                 tags=ALLOWED_HTML_TAGS,
    #                 attributes=ALLOWED_HTML_ATTRS,
    #                 strip=True
    #             )

    #     # Sanitize implementation guides
    #     if self.implementations:
    #         for guide in self.implementations:
    #             guide.description = bleach.clean(
    #                 guide.description,
    #                 tags=ALLOWED_HTML_TAGS,
    #                 attributes=ALLOWED_HTML_ATTRS,
    #                 strip=True
    #             )

    #     # Normalize tags
    #     if self.tags:
    #         self.tags = list(set(tag.lower().strip() for tag in self.tags if tag))

    # @before_event([Insert, Replace])
    # def validate_content_lengths(self) -> None:
    #     """Validates content lengths before saving.
        
    #     Raises:
    #         ValueError: If content exceeds maximum allowed length
    #     """
    #     if len(self.name) > MAX_NAME_LENGTH:
    #         raise ValueError(f"Name exceeds maximum length of {MAX_NAME_LENGTH} characters")
            
    #     if len(self.description) > MAX_DESCRIPTION_LENGTH:
    #         raise ValueError(f"Description exceeds maximum length of {MAX_DESCRIPTION_LENGTH} characters")
            
    #     if self.overview and len(self.overview) > MAX_OVERVIEW_LENGTH:
    #         raise ValueError(f"Overview exceeds maximum length of {MAX_OVERVIEW_LENGTH} characters")
    #         for item in self.troubleshooting:
    #             if item.description:
    #                 item.description = bleach.clean(item.description)
    #             if item.solution:
    #                 item.solution = bleach.clean(item.solution)
                    
    #     # Sanitize best practices
    #     if self.best_practices:
    #         for practice in self.best_practices:
    #             if practice.description:
    #                 practice.description = bleach.clean(practice.description)
                    
    #     # Sanitize implementation guides
    #     if self.implementations:
    #         for impl in self.implementations:
    #             if impl.description:
    #                 impl.description = bleach.clean(impl.description)
    #             if isinstance(impl.steps, list):
    #                 impl.steps = [bleach.clean(str(step)) for step in impl.steps if step]

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
