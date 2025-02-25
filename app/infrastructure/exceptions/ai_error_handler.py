"""
AI Error Handler Module

This module provides a centralized error handling mechanism for AI operations.
It follows the 3:1:1 rule for code structure, testability, and maintainability:
- 3 parts focused on clear code structure and organization
- 1 part focused on testability with proper error context
- 1 part focused on maintainability with detailed logging
"""

from typing import TypeVar, Callable, Any, Dict
from functools import wraps
import logging
from datetime import datetime

from .ai_exceptions import (
    AIException,
    ModelInferenceError,
    ContentGenerationError,
    ValidationError,
    TokenLimitError
)

T = TypeVar('T')
logger = logging.getLogger(__name__)

class AIErrorHandler:
    """Handles AI operation errors with structured logging and error mapping"""

    @staticmethod
    def _get_operation_context(func: Callable, args: tuple, kwargs: Dict) -> Dict[str, Any]:
        """Extract operation context from function call.
        
        This helps with testability by providing consistent error context.
        """
        return {
            "operation": func.__name__.lstrip('_'),
            "timestamp": datetime.now().isoformat(),
            "args": args,
            "kwargs": kwargs
        }

    @staticmethod
    def _map_exception(e: Exception, context: Dict[str, Any]) -> AIException:
        """Map generic exceptions to specific AI exceptions.
        
        This improves maintainability by centralizing exception mapping logic.
        """
        error_msg = str(e).lower()
        
        if "token" in error_msg:
            return TokenLimitError(
                message=f"Token limit exceeded: {str(e)}",
                current_tokens=context.get("current_tokens", 0),
                max_tokens=context.get("max_tokens", 0)
            )
        elif "model" in error_msg or "inference" in error_msg:
            return ModelInferenceError(
                message=f"Model inference failed: {str(e)}",
                model_name=context.get("model_name", "unknown"),
                input_data=context.get("input_data", {})
            )
        elif "validation" in error_msg:
            return ValidationError(
                message=f"Content validation failed: {str(e)}",
                content_type=context.get("content_type", "unknown"),
                validation_errors=context.get("validation_errors", {})
            )
        elif "generation" in error_msg or "content" in error_msg:
            return ContentGenerationError(
                message=f"Content generation failed: {str(e)}",
                content_type=context.get("content_type", "unknown"),
                parameters=context.get("parameters", {})
            )
        else:
            return AIException(
                message=f"AI operation failed: {str(e)}",
                operation=context.get("operation")
            )

    @staticmethod
    def handle_operation(func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for handling AI operations errors with structured logging.
        
        This improves code structure by separating error handling from business logic.
        """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Get operation context for better error tracking
            context = AIErrorHandler._get_operation_context(func, args, kwargs)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log error with full context
                logger.error(
                    f"AI error in operation '{context['operation']}': {str(e)}",
                    extra=context,
                    exc_info=True
                )
                
                # Convert to appropriate AI exception
                if isinstance(e, AIException):
                    raise
                
                raise AIErrorHandler._map_exception(e, context)
                
        return wrapper
