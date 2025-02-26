"""Base response schemas."""

from typing import List, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Provides a structure for paginated responses."""
    items: List[T]
    total: int
    skip: int
    limit: int
