from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.users import UserRepository
from ..schemas.users import UserCreate, UserUpdate, UserResponse
from ..models.users import User
from ..exceptions.base import (
    NotFoundException,
    DuplicateException,
    UnauthorizedException,
    ValidationException
)

class UserService:
    """Service layer for managing user operations with business logic"""

    def __init__(self, db: AsyncSession):
        """Initialize service with databse session"""
        self.repository = UserRepository(db)

    async def validate_unique(self, field: str, value: any, exclude_id: Optional[int] = None) -> None:
        """Validate unique constraints for user fields

        Args:
            field: Field name to validate
            value: Value to check for uniqueness
            exclude_id: Optional ID to exclude from uniqueness check

        Raises:
            DuplicateException: If value already exists for the field
        """
        if field == "email":
            existing_user = await self.repository.get_by_email(value)
            if existing_user and (exclude_id is None or existing_user.id != exclude_id):
                raise DuplicateException(f"User with {field} {value} already exists")

    async def create(self, user_data: UserCreate) -> UserResponse:
        """Create a new user with validation

        Args:
            user_data: User creation data

        Returns:
            UserResponse: Created user data

        Raises:
            DuplicateException: If user with same email already exists
        """
        await self.validate_unique("email", user_data.email)
        user = await self.repository.create(user_data)
        return UserResponse.model_validate(user)

    async def get(self, user_id: int) -> UserResponse:
        """Get a user by ID

        Args:
            user_id: ID of the user to retrieve

        Returns:
            UserResponse: User data

        Raises:
            NotFoundException: If user does not exist
        """
        user = await self.repository.get(user_id)
        return UserResponse.model_validate(user)

    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        """Get a user by email

        Args:
            email: Email of the user to retrieve

        Returns:
            Optional[UserResponse]: User data if found, None otherwise
        """
        user = await self.repository.get_by_email(email)
        return UserResponse.model_validate(user) if user else None

    async def list(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """List users with pagination

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[UserResponse]: List of users

        Raises:
            ValidationException: If pagination parameters are invalid
        """
        if skip < 0:
            raise ValidationException("Skip parameter cannot be negative")
        if limit < 1:
            raise ValidationException("Limit parameter must be greater than 0")

        users = await self.repository.list(skip=skip, limit=limit)
        return [UserResponse.model_validate(user) for user in users]

    async def update(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        """Update a user with validation

        Args:
            user_id: ID of the user to update
            user_data: New user data

        Returns:
            UserResponse: Updated user data

        Raises:
            NotFoundException: If user does not exist
            DuplicateException: If trying to update email to one that already exists
        """
        if user_data.email:
            await self.validate_unique("email", user_data.email, exclude_id=user_id)

        user = await self.repository.update(user_id, user_data)
        return UserResponse.model_validate(user)

    async def delete(self, user_id: int) -> None:
        """Delete a user

        Args:
            user_id: ID of the user to delete

        Raises:
            NotFoundException: If user does not exist
        """
        await self.repository.delete(user_id)

    async def authenticate(self, email: str, password: str) -> UserResponse:
        """Authenticate a user

        Args:
            email: User's email
            password: User's password

        Returns:
            UserResponse: Authenticated user data

        Raises:
            UnauthorizedException: If credentials are invalid
        """
        user = await self.repository.authenticate(email, password)
        if not user:
            raise UnauthorizedException("Invalid email or password")
        return UserResponse.model_validate(user)
