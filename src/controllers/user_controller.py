import logging
from fastapi import APIRouter, HTTPException, Path, Body, Query, status
from src.models.user import User, CreateUser
from database.schemas.user_schema import UserSchema
from typing import List, Optional, Dict, Any
from database.database import users_collection

logger = logging.getLogger("hydration_tracker.controllers")

router = APIRouter(tags=["user"])
schema = UserSchema()


@router.post("/user/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUser = Body(...)):
    """
    Create a new user in the database.

    This endpoint receives a CreateUser object from the request body and attempts to create a new user in the database.
    If successful, it returns the created user data with an ID.

    Args:
        user: A CreateUser object containing the user's name and weight,
              passed as JSON in the request body.

    Returns:
        User: The created user data with an ID, returned as JSON in the response body.
    """
    # Log the creation attempt
    logger.info(f"Creating new user: {user.name}")

    # Attempt to create the user in the database
    try:
        # Call the UserSchema.create_user method to create the user
        return schema.create_user(user)
        return schema.create_user(user)
    except HTTPException as e:
        # If an HTTPException (like 404 or 409) is raised, re-raise it
        raise
    except Exception as e:
        # If any other exception is raised, log the error and return a 500 error
        logger.error(f"Unexpected error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user",
        )


@router.get("/user/{user_id}/", response_model=User)
async def get_user(
    user_id: str = Path(..., description="The ID of the user to retrieve")
):
    """
    Get user data by ID.

    Args:
        user_id: The ID of the user to retrieve

    Returns:
        User: User data with ID
    """
    try:
        logger.info(f"Getting user: {user_id}")
        return schema.get_user(user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the user",
        )


@router.put("/user/{user_id}/", response_model=User)
async def update_user(
    user_id: str = Path(..., description="The ID of the user to update"),
    update_data: Dict[str, Any] = Body(..., description="User data to update"),
):
    """
    Update user data by ID.

    Args:
        user_id: The ID of the user to update
        update_data: User data fields to update

    Returns:
        User: Updated user data
    """
    try:
        logger.info(f"Updating user: {user_id}")
        return schema.update_user(user_id, update_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the user",
        )


@router.delete("/user/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str = Path(..., description="The ID of the user to delete")
):
    """
    Delete a user and all their trackers.

    Args:
        user_id: The ID of the user to delete
    """
    try:
        logger.info(f"Deleting user: {user_id}")
        schema.delete_user(user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the user",
        )


@router.get("/users/", response_model=List[User])
async def list_users(
    limit: Optional[int] = Query(None, description="Limit the number of users returned"),
    skip: Optional[int] = Query(0, description="Skip the first N users"),
    name: Optional[str] = Query(None, description="Filter users by name"),
):
    """
    Get all users data with optional filtering.

    Args:
        limit: Maximum number of users to return
        skip: Number of users to skip
        name: Filter users by name (case-insensitive substring match)

    Returns:
        List[User]: List of users
    """
    try:
        logger.info(f"Listing users with filters: limit={limit}, skip={skip}, name={name}")

        # Build query
        query = {}
        if name:
            query["name"] = {"$regex": name, "$options": "i"}

        # Get users from database
        users = schema.users_serializer(
            users_collection.find(query).skip(skip).limit(limit) if limit else users_collection.find(query).skip(skip)
        )

        return users
    except Exception as e:
        logger.error(f"Unexpected error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving users",
        )