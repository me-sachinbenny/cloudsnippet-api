"""
Repository Exception Module

This module defines custom exceptions for repository operations to provide
better error handling and more specific error messages.
"""

from fastapi import HTTPException, status

class RepositoryException(Exception):
    """Base exception for repository operations"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DuplicateEntityException(RepositoryException):
    """Raised when attempting to create a duplicate entity"""
    def __init__(self, entity_type: str, identifier: str, value: str):
        self.entity_type = entity_type
        self.identifier = identifier
        self.value = value
        message = f"{entity_type} with {identifier} '{value}' already exists"
        super().__init__(message)

    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=self.message
        )

class EntityNotFoundException(RepositoryException):
    """Raised when an entity is not found"""
    def __init__(self, entity_type: str, identifier: str, value: str):
        self.entity_type = entity_type
        self.identifier = identifier
        self.value = value
        message = f"{entity_type} with {identifier} '{value}' not found"
        super().__init__(message)

    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=self.message
        )

class InvalidIdentifierException(RepositoryException):
    """Raised when an invalid identifier format is provided"""
    def __init__(self, identifier_type: str, value: str):
        self.identifier_type = identifier_type
        self.value = value
        message = f"Invalid {identifier_type} format: {value}"
        super().__init__(message)

    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.message
        )
