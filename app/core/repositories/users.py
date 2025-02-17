from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models.users import User
from ..schemas.users import UserCreate, UserUpdate
from ..security import get_password_hash, verify_password
from ..exceptions.base import NotFoundException, DuplicateException

class UserRepository:
    """Repository for managing user data in the database"""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session"""
        self.db = db

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user in the database"""
        try:
            user = User(
                email=user_data.email,
                name=user_data.name,
                hashed_password=get_password_hash(user_data.password),
                is_active=True
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateException(f"User with email {user_data.email} already exists")

    async def get(self, user_id: int) -> User:
        """Get a user by ID"""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get a list of users with pagination"""
        query = select(User).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, user_id: int, user_data: UserUpdate) -> User:
        """Update a user's information"""
        try:
            user = await self.get(user_id)
            
            update_data = user_data.model_dump(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

            for field, value in update_data.items():
                setattr(user, field, value)

            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateException("Email already exists")

    async def delete(self, user_id: int) -> None:
        """Delete a user from the database"""
        user = await self.get(user_id)
        await self.db.delete(user)
        await self.db.commit()

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password"""
        user = await self.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
