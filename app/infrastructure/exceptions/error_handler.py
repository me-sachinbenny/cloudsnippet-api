"""
Error Handler Module

This module provides a centralized error handling mechanism for repository operations.
It converts database and application exceptions into appropriate HTTP responses.
"""

from typing import TypeVar, Callable, Any
from functools import wraps
from pymongo.errors import DuplicateKeyError
from bson.errors import InvalidId

from .repository_exceptions import (
    DuplicateEntityException,
    EntityNotFoundException,
    InvalidIdentifierException
)

T = TypeVar('T')

class RepositoryErrorHandler:
    """Handles repository operation errors and converts them to appropriate exceptions"""

    @staticmethod
    def handle_operation(func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for handling repository operations errors"""
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)
            except DuplicateKeyError as e:
                # Extract entity details from the first argument (self) and kwargs
                entity_type = args[0].__class__.__name__.replace('Repository', '')
                # Try to get the name from kwargs or use a default identifier
                identifier = next((v for k, v in kwargs.items() if 'name' in k.lower()), 'identifier')
                raise DuplicateEntityException(entity_type, "name", str(identifier))
            except InvalidId as e:
                raise InvalidIdentifierException("ID", str(e))
            except Exception as e:
                # Re-raise known custom exceptions
                if isinstance(e, (DuplicateEntityException, EntityNotFoundException, InvalidIdentifierException)):
                    raise
                # For unknown exceptions, raise a generic repository exception
                raise Exception(f"Repository operation failed: {str(e)}")
        return wrapper
