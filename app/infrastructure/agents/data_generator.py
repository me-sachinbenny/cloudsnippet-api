"""AI Data Generator for Tool Content

This module implements the AI-powered data generation system for tool content:
- Generates initial tool content using LLMs
- Processes review requests and updates
- Manages the AI workflow for content enhancement

Design Principles:
- Clear separation of concerns between content generation and workflow
- Testable components with well-defined interfaces
- Maintainable code structure with consistent patterns
- Efficient error handling and validation
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import logging

# Third-party imports
from langgraph.graph import StateGraph, START, END
from langchain_openai import OpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Application imports
from ...schemas.tool_schemas import (
    CreateToolRequest,
    ToolState,
    BestPractice,
    TroubleshootingItem,
    Solution,
    RootCause
)
from ..repositories.tools_repository import ToolsRepository
from ..exceptions.ai_error_handler import AIErrorHandler
from ..exceptions.ai_exceptions import (
    ModelInferenceError,
    ContentGenerationError,
    ValidationError,
    TokenLimitError
)

# Configure logging
logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------------

DEFAULT_MODEL = "gpt-4-turbo"
DEFAULT_TEMPERATURE = 0

PROMPT_TEMPLATES = {
    "system": "You are an AI assistant that generates structured content for developer tools.",
    "tool": """
        Generate comprehensive documentation for {tool_name} including:
        1. Brief description (1-2 sentences)
        2. Catchy tagline
        3. Detailed overview
        4. Category classification
        5. Common troubleshooting issues (2-3 items)
        6. Best practices (3-4 items)
        7. Relevant tags
        
        Format the response as a JSON object with these exact keys.
        Make sure troubleshooting items include title, description, severity, and solution steps.
    """
}

#-----------------------------------------------------------------------------
# AI Data Generator
#-----------------------------------------------------------------------------

class AI_Data_Generator:
    """AI-powered content generation and processing for tools.
    
    This class handles the generation of tool documentation and content using LLMs.
    It follows a structured approach to ensure consistent and high-quality output.
    
    Attributes:
        repository: Repository for tool data persistence
        llm: Language model instance for content generation
    """
    
    def __init__(
        self,
        repository: ToolsRepository,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE
    ):
        """Initialize the generator with repository and model settings."""
        self.repository = repository
        self.llm = OpenAI(model=model, temperature=temperature)

    @AIErrorHandler.handle_operation
    async def initial_query(self, tool_name: str) -> CreateToolRequest:
        """Generate initial tool data using AI.
        
        Args:
            tool_name: Name of the tool to generate data for
            
        Returns:
            CreateToolRequest with generated data
            
        Raises:
            ValidationError: If tool name is empty
            ModelInferenceError: If AI model fails
            ContentGenerationError: If content generation fails
        """
        if not tool_name or not tool_name.strip():
            raise ValidationError(
                message="Tool name cannot be empty",
                content_type="tool_name",
                validation_errors={"tool_name": "Empty or whitespace"}
            )
            
        # Setup messages for AI query
        messages = self._create_messages(tool_name)
        
        # Get AI response
        response = await self._get_ai_response(messages)
        
        # Parse and validate response
        parsed_data = self._parse_ai_response(response)
        
        # Create and return tool request
        return self._create_tool_request(tool_name, parsed_data)

    def _create_messages(self, tool_name: str) -> List[Dict[str, str]]:
        """Create message list for AI query."""
        return [
            SystemMessage(content=PROMPT_TEMPLATES["system"]),
            HumanMessage(content=PROMPT_TEMPLATES["tool"].format(tool_name=tool_name))
        ]

    @AIErrorHandler.handle_operation
    async def _get_ai_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from AI model with error handling.
        
        Args:
            messages: List of messages for the AI model
            
        Returns:
            Model response as string
            
        Raises:
            ModelInferenceError: If model call fails
            TokenLimitError: If token limit is exceeded
        """
        try:
            return await self.llm.ainvoke(messages)
        except Exception as e:
            if "token" in str(e).lower():
                raise TokenLimitError(
                    message="Token limit exceeded in model call",
                    current_tokens=len(str(messages)),
                    max_tokens=4096  # Adjust based on model
                )
            raise ModelInferenceError(
                message="Model inference failed",
                model_name=self.llm.model_name,
                input_data={"messages": messages}
            )

    @AIErrorHandler.handle_operation
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate AI response.
        
        Args:
            response: Raw response string from AI model
            
        Returns:
            Parsed and validated response data
            
        Raises:
            ContentGenerationError: If response parsing fails
            ValidationError: If response validation fails
        """
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            raise ContentGenerationError(
                message="Invalid JSON in AI response",
                content_type="json",
                parameters={"error": str(e), "response": response[:100]}
            )
            
        self._validate_response_data(data)
        return data

    @AIErrorHandler.handle_operation
    def _validate_response_data(self, data: Dict[str, Any]) -> None:
        """Validate required fields in response data.
        
        Args:
            data: Response data to validate
            
        Raises:
            ValidationError: If required fields are missing
        """
        required_fields = ["description", "tagline", "overview", "category"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            raise ValidationError(
                message="Missing required fields in response",
                content_type="response_data",
                validation_errors={
                    "missing_fields": missing_fields,
                    "provided_fields": list(data.keys())
                }
            )

    @AIErrorHandler.handle_operation
    def _create_tool_request(self, tool_name: str, data: Dict[str, Any]) -> CreateToolRequest:
        """Create tool request from validated data.
        
        Args:
            tool_name: Name of the tool
            data: Validated data for tool creation
            
        Returns:
            CreateToolRequest instance
            
        Raises:
            ValidationError: If data validation fails
        """
        try:
            return CreateToolRequest(
                name=tool_name,
                slug=self._generate_slug(tool_name),
                description=data["description"],
                image=data.get("image"),
                overview=data["overview"],
                tagline=data["tagline"],
                category=data["category"],
                troubleshooting=self._create_troubleshooting_items(data.get("troubleshooting", [])),
                best_practices=self._create_best_practices(data.get("best_practices", [])),
                tags=data.get("tags", [])
            )
        except KeyError as e:
            raise ValidationError(
                message="Missing required field in tool request",
                content_type="tool_request",
                validation_errors={"missing_field": str(e)}
            )

    @staticmethod
    def _generate_slug(name: str) -> str:
        """Generate URL-friendly slug from name."""
        return name.lower().replace(" ", "-")

    @AIErrorHandler.handle_operation
    def _create_troubleshooting_items(self, items: list) -> List[TroubleshootingItem]:
        """Create troubleshooting items with proper validation.
        
        Args:
            items: List of troubleshooting item data
            
        Returns:
            List of TroubleshootingItem instances
            
        Raises:
            ValidationError: If item validation fails
        """
        try:
            return [
                TroubleshootingItem(
                    id=self._generate_id("tr", i),
                    title=self._get_required(item, "title", f"Troubleshooting item {i+1}"),
                    description=self._get_required(item, "description", f"Troubleshooting item {i+1}"),
                    severity=item.get("severity", "medium"),
                    symptoms=item.get("symptoms", []),
                    root_cause=self._create_root_cause(item.get("root_cause", {})),
                    solution=self._create_solution(item.get("solution", {}))
                )
                for i, item in enumerate(items)
            ]
        except Exception as e:
            raise ValidationError(
                message="Failed to create troubleshooting items",
                content_type="troubleshooting_items",
                validation_errors={"error": str(e), "items": items}
            )

    @AIErrorHandler.handle_operation
    def _create_best_practices(self, items: list) -> List[BestPractice]:
        """Create best practices with validation.
        
        Args:
            items: List of best practice data
            
        Returns:
            List of BestPractice instances
            
        Raises:
            ValidationError: If item validation fails
        """
        try:
            return [
                BestPractice(
                    id=self._generate_id("bp", i),
                    title=self._get_required(item, "title", f"Best practice {i+1}"),
                    description=self._get_required(item, "description", f"Best practice {i+1}")
                )
                for i, item in enumerate(items)
            ]
        except Exception as e:
            raise ValidationError(
                message="Failed to create best practices",
                content_type="best_practices",
                validation_errors={"error": str(e), "items": items}
            )

    @staticmethod
    def _generate_id(prefix: str, index: int) -> str:
        """Generate unique ID for items."""
        return f"{prefix}_{index + 1}"

    @staticmethod
    @AIErrorHandler.handle_operation
    def _get_required(data: Dict[str, Any], field: str, context: str) -> str:
        """Get required field with validation.
        
        Args:
            data: Dictionary containing the field
            field: Name of the required field
            context: Context for error messages
            
        Returns:
            Value of the required field
            
        Raises:
            ValidationError: If field is missing or empty
        """
        value = data.get(field, "")
        if not value:
            raise ValidationError(
                message=f"Missing required field: {field}",
                content_type="required_field",
                validation_errors={
                    "field": field,
                    "context": context,
                    "provided_data": data
                }
            )
        return value

    @AIErrorHandler.handle_operation
    def _create_root_cause(self, data: Dict[str, Any]) -> RootCause:
        """Create root cause with validation.
        
        Args:
            data: Root cause data
            
        Returns:
            RootCause instance
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            return RootCause(
                description=data.get("description", ""),
                factors=data.get("factors", [])
            )
        except Exception as e:
            raise ValidationError(
                message="Failed to create root cause",
                content_type="root_cause",
                validation_errors={"error": str(e), "data": data}
            )

    @AIErrorHandler.handle_operation
    def _create_solution(self, data: Dict[str, Any]) -> Solution:
        """Create solution with validation.
        
        Args:
            data: Solution data
            
        Returns:
            Solution instance
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            return Solution(
                steps=data.get("steps", []),
                prevention_tips=data.get("prevention_tips", [])
            )
        except Exception as e:
            raise ValidationError(
                message="Failed to create solution",
                content_type="solution",
                validation_errors={"error": str(e), "data": data}
            )

