from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

# Define generic types for models
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)

class BaseService(ABC, Generic[CreateSchemaType, UpdateSchemaType, ResponseSchemaType]):
    """
    Abstract base service defining the interface for all services.
    This ensures consistent CRUD operations across different services.
    """
    
    @abstractmethod
    async def create(self, data: CreateSchemaType) -> ResponseSchemaType:
        """Create a new resource"""
        pass

    @abstractmethod
    async def get(self, id: int) -> ResponseSchemaType:
        """Get a resource by ID"""
        pass

    @abstractmethod
    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[ResponseSchemaType]:
        """List resources with pagination and optional filters"""
        pass

    @abstractmethod
    async def update(
        self,
        id: int,
        data: UpdateSchemaType
    ) -> ResponseSchemaType:
        """Update a resource"""
        pass

    @abstractmethod
    async def delete(self, id: int) -> None:
        """Delete a resource"""
        pass

    async def exists(self, id: int) -> bool:
        """Check if a resource exists"""
        try:
            await self.get(id)
            return True
        except:
            return False

    async def validate_unique(
        self,
        field: str,
        value: any,
        exclude_id: Optional[int] = None
    ) -> None:
        """
        Validate that a field value is unique.
        Implement in child classes if needed.
        """
        pass
