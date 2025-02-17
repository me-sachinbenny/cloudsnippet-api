from fastapi import APIRouter, Depends, status
from typing import List, Optional
from ....core.models.users import UserCreate, UserUpdate, UserResponse
from ....core.services.users import UserService
from ....core.repositories.users import UserRepository

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Resource not found"},
        status.HTTP_409_CONFLICT: {"description": "Resource already exists"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"}
    }
)

def get_user_service() -> UserService:
    """Dependency injection for UserService"""
    return UserService(UserRepository())

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with the provided data. Email must be unique."
)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return await service.create(user_data)

@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List all users",
    description="Get all users with pagination. Use skip and limit for pagination control."
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service)
) -> List[UserResponse]:
    return await service.list(skip=skip, limit=limit)

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a specific user by their unique identifier."
)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return await service.get(user_id)

@router.get(
    "/email/{email}",
    response_model=Optional[UserResponse],
    summary="Get user by email",
    description="Retrieve a user by their email address."
)
async def get_user_by_email(
    email: str,
    service: UserService = Depends(get_user_service)
) -> Optional[UserResponse]:
    return await service.get_by_email(email)

@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update a user's information. Email must remain unique."
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return await service.update(user_id, user_data)

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user by their ID. Returns 204 if successful."
)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
) -> None:
    await service.delete(user_id)

@router.post(
    "/authenticate",
    response_model=UserResponse,
    summary="Authenticate user",
    description="Authenticate a user with email and password."
)
async def authenticate_user(
    email: str,
    password: str,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    user = await service.authenticate(email, password)
    return UserResponse.model_validate(user)
