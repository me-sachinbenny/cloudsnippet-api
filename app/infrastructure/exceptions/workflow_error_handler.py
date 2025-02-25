"""
Workflow Error Handler Module

This module provides a centralized error handling mechanism for workflow operations.
It converts workflow-specific exceptions into appropriate responses and handles logging.
"""

from typing import TypeVar, Callable, Any
from functools import wraps
import logging
from datetime import datetime

from .workflow_exceptions import (
    WorkflowException,
    WorkflowStateError,
    ContentProcessingError,
    WorkflowConfigurationError,
    ReviewActionError
)

T = TypeVar('T')
logger = logging.getLogger(__name__)

class WorkflowErrorHandler:
    """Handles workflow operation errors and provides logging"""

    @staticmethod
    def handle_operation(func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for handling workflow operations errors"""
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get workflow step name from function name
                step = func.__name__.lstrip('_')
                
                # Log the error with context
                logger.error(
                    f"Workflow error in step '{step}': {str(e)}",
                    extra={
                        "step": step,
                        "timestamp": datetime.now().isoformat(),
                        "args": args,
                        "kwargs": kwargs
                    },
                    exc_info=True
                )
                
                # Convert to appropriate workflow exception
                if isinstance(e, WorkflowException):
                    raise
                
                # Map different error types to specific workflow exceptions
                if "state" in str(e).lower():
                    raise WorkflowStateError(
                        message=f"Invalid state transition: {str(e)}",
                        step=step,
                        current_state=kwargs.get("state", {})
                    )
                elif "content" in str(e).lower():
                    raise ContentProcessingError(
                        message=f"Content processing failed: {str(e)}",
                        step=step,
                        content_type=kwargs.get("content_type", "unknown")
                    )
                elif "action" in str(e).lower():
                    raise ReviewActionError(
                        message=f"Review action processing failed: {str(e)}",
                        step=step,
                        action_id=kwargs.get("action_id", "unknown"),
                        action_details=kwargs.get("action_details", {})
                    )
                else:
                    raise WorkflowException(
                        message=f"Workflow operation failed: {str(e)}",
                        step=step
                    )
                
        return wrapper
