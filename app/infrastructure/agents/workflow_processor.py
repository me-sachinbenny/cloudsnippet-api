"""AI Workflow Processor for Tool Content

This module implements the workflow processing system for tool content:
- Manages the state transitions for content processing
- Handles review actions and updates
- Ensures data consistency throughout the workflow

Design Principles:
- Clear separation of workflow logic from content generation
- Testable state transitions
- Maintainable workflow definitions
- Efficient error handling
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
from datetime import datetime
from typing import Dict, Any, List
import logging

# Third-party imports
from langgraph.graph import StateGraph, START, END

# Application imports
from ...schemas.tool_schemas import (
    ToolState,
    BestPractice,
    TroubleshootingItem,
    Solution,
    RootCause
)

# Configure logging
logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------------

WORKFLOW_STEPS = {
    "process_content": "Initial content processing",
    "update_best_practices": "Best practices enhancement",
    "update_troubleshooting": "Troubleshooting enhancement"
}

#-----------------------------------------------------------------------------
# Workflow Processor
#-----------------------------------------------------------------------------

# Import error handling
from ..exceptions.workflow_error_handler import WorkflowErrorHandler
from ..exceptions.workflow_exceptions import WorkflowConfigurationError

class WorkflowProcessor:
    """Manages the workflow for processing tool content."""
    
    @staticmethod
    @WorkflowErrorHandler.handle_operation
    def create_workflow() -> StateGraph:
        """Create a workflow graph for processing tool state.
        
        Returns:
            StateGraph: Configured workflow graph
            
        Raises:
            WorkflowConfigurationError: If workflow creation fails
        """
        workflow = StateGraph(ToolState)
        
        # Add processing nodes
        for step, description in WORKFLOW_STEPS.items():
            logger.info(f"Adding workflow step: {description}")
            workflow.add_node(step, getattr(WorkflowProcessor, f"_{step}"))
        
        # Define workflow edges
        edges = [
            (START, "process_content"),
            ("process_content", "update_best_practices"),
            ("update_best_practices", "update_troubleshooting"),
            ("update_troubleshooting", END)
        ]
        
        for source, target in edges:
            try:
                workflow.add_edge(source, target)
            except Exception as e:
                raise WorkflowConfigurationError(
                    message=f"Failed to add edge {source} -> {target}",
                    config_details={
                        "source": source,
                        "target": target,
                        "error": str(e)
                    }
                )
        
        return workflow

    @staticmethod
    @WorkflowErrorHandler.handle_operation
    def _process_content(state: ToolState) -> ToolState:
        """Process and validate initial tool content.
        
        Args:
            state: Current tool state
            
        Returns:
            ToolState: Updated tool state
            
        Raises:
            ContentProcessingError: If content processing fails
        """
        logger.info(f"Processing content for tool: {state.tool_id}")
        state.updated_at = datetime.now()
        return state

    @staticmethod
    @WorkflowErrorHandler.handle_operation
    def _update_best_practices(state: ToolState) -> ToolState:
        """Update best practices based on review actions.
        
        Args:
            state: Current tool state
            
        Returns:
            ToolState: Updated tool state with new best practices
            
        Raises:
            ReviewActionError: If processing review actions fails
        """
        for action in state.review_actions:
            if (action.task == "approve_with_updates" and 
                "best practice" in action.details.lower()):
                logger.info(f"Adding best practice from action: {action.details}")
                state.best_practices.append(
                    BestPractice(
                        id=f"bp_{len(state.best_practices) + 1}",
                        title=action.details,
                        description="AI generated best practice"
                    )
                )
        return state

    @staticmethod
    @WorkflowErrorHandler.handle_operation
    def _update_troubleshooting(state: ToolState) -> ToolState:
        """Update troubleshooting based on review actions.
        
        Args:
            state: Current tool state
            
        Returns:
            ToolState: Updated tool state with new troubleshooting items
            
        Raises:
            ReviewActionError: If processing review actions fails
        """
        for action in state.review_actions:
            if (action.task == "approve_with_updates" and 
                "troubleshooting" in action.details.lower()):
                logger.info(f"Adding troubleshooting from action: {action.details}")
                state.troubleshooting.append(
                    TroubleshootingItem(
                        id=f"tr_{len(state.troubleshooting) + 1}",
                        title=action.details,
                        description="AI generated troubleshooting",
                        severity="medium",
                        symptoms=[],
                        root_cause=RootCause(
                            description="",
                            factors=[]
                        ),
                        solution=Solution(
                            steps=[],
                            prevention_tips=[]
                        )
                    )
                )
        return state
