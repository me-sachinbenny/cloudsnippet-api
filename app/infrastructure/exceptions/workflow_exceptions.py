"""
Workflow Exception Module

This module defines custom exceptions for workflow operations to provide
better error handling and more specific error messages for the AI workflow system.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status

class WorkflowException(Exception):
    """Base exception for workflow operations"""
    def __init__(self, message: str, step: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.step = step
        self.details = details or {}
        super().__init__(self.message)

    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": self.message,
                "step": self.step,
                "details": self.details
            }
        )

class WorkflowStateError(WorkflowException):
    """Raised when there's an error in workflow state transition"""
    def __init__(self, message: str, step: str, current_state: Dict[str, Any]):
        super().__init__(
            message=message,
            step=step,
            details={"current_state": current_state}
        )

class ContentProcessingError(WorkflowException):
    """Raised when content processing fails"""
    def __init__(self, message: str, step: str, content_type: str):
        super().__init__(
            message=message,
            step=step,
            details={"content_type": content_type}
        )

class WorkflowConfigurationError(WorkflowException):
    """Raised when there's an error in workflow configuration"""
    def __init__(self, message: str, config_details: Dict[str, Any]):
        super().__init__(
            message=message,
            details={"configuration": config_details}
        )

class ReviewActionError(WorkflowException):
    """Raised when there's an error processing review actions"""
    def __init__(self, message: str, step: str, action_id: str, action_details: Dict[str, Any]):
        super().__init__(
            message=message,
            step=step,
            details={
                "action_id": action_id,
                "action_details": action_details
            }
        )
