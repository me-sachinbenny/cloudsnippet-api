"""
AI Exception Module

This module defines custom exceptions for AI operations to provide
better error handling and more specific error messages for the AI data generation system.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status

class AIException(Exception):
    """Base exception for AI operations"""
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.operation = operation
        self.details = details or {}
        super().__init__(self.message)

    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": self.message,
                "operation": self.operation,
                "details": self.details
            }
        )

class ModelInferenceError(AIException):
    """Raised when AI model inference fails"""
    def __init__(self, message: str, model_name: str, input_data: Dict[str, Any]):
        super().__init__(
            message=message,
            operation="model_inference",
            details={
                "model_name": model_name,
                "input_data": input_data
            }
        )

class ContentGenerationError(AIException):
    """Raised when content generation fails"""
    def __init__(self, message: str, content_type: str, parameters: Dict[str, Any]):
        super().__init__(
            message=message,
            operation="content_generation",
            details={
                "content_type": content_type,
                "parameters": parameters
            }
        )

class ValidationError(AIException):
    """Raised when generated content validation fails"""
    def __init__(self, message: str, content_type: str, validation_errors: Dict[str, Any]):
        super().__init__(
            message=message,
            operation="content_validation",
            details={
                "content_type": content_type,
                "validation_errors": validation_errors
            }
        )

class TokenLimitError(AIException):
    """Raised when token limit is exceeded"""
    def __init__(self, message: str, current_tokens: int, max_tokens: int):
        super().__init__(
            message=message,
            operation="token_validation",
            details={
                "current_tokens": current_tokens,
                "max_tokens": max_tokens
            }
        )
