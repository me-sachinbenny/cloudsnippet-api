from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .base import AppException
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ErrorResponse:
    """Standardized error response"""
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
        extra: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.extra = extra or {}

    def to_dict(self) -> dict:
        return {
            "error": {
                "message": self.message,
                "code": self.code,
                **({"details": self.extra} if self.extra else {})
            }
        }

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions"""
    error = ErrorResponse(
        message=exc.message,
        code=exc.__class__.__name__,
        status_code=exc.status_code,
        extra=exc.extra
    )
    
    # Log error for debugging
    logger.error(
        f"AppException occurred: {error.to_dict()}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error.to_dict()
    )

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle pydantic validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join([str(x) for x in error["loc"]]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error = ErrorResponse(
        message="Validation error",
        code="RequestValidationError",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        extra={"validation_errors": errors}
    )
    
    logger.warning(
        f"Validation error occurred: {error.to_dict()}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error.to_dict()
    )

async def python_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected Python exceptions"""
    error = ErrorResponse(
        message="Internal server error",
        code="InternalServerError",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        extra={"type": exc.__class__.__name__}
    )
    
    # Log the full error for debugging
    logger.exception(
        f"Unexpected error occurred: {str(exc)}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error.to_dict()
    )
