from typing import Any, Dict, Optional
from fastapi import status

class AppException(Exception):
    """Base exception for application"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        extra: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.extra = extra or {}
        super().__init__(message)

class NotFoundException(AppException):
    """Resource not found"""
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            message=f"{resource} with id {resource_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

class ValidationException(AppException):
    """Validation error"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class DuplicateException(AppException):
    """Duplicate resource"""
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            message=f"{resource} with {field} '{value}' already exists",
            status_code=status.HTTP_409_CONFLICT
        )

class UnauthorizedException(AppException):
    """Unauthorized access"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class ForbiddenException(AppException):
    """Forbidden access"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )
