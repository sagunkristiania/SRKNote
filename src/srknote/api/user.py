"""
user.py
--------
This module provides endpoints for managing user profiles in the SRKNote application.

Features:
- Check login status
- Retrieve user profile
- Edit user profile (name, email, password)
- Delete user account

All endpoints require authentication through JWT tokens, ensuring only
the logged-in user can modify or delete their own data.
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, SecretStr

from ..config.db import get_db
from ..config.security import get_current_user, hash_password as get_password_hash
from ..repository.UserRepository import UserRepository
from ..models.User import User

# Define router for all user-related endpoints
router = APIRouter(prefix="/api/v1/users", tags=["Users"])


# -------------------------
# Pydantic Schemas
# -------------------------
class UserResponse(BaseModel):
    """
    Response model representing basic user details.
    """
    id: UUID
    name: str
    email: EmailStr


class UserUpdate(BaseModel):
    """
    Request model for updating user information.
    Fields are optional to allow partial updates.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[SecretStr] = None


# -------------------------
# API Endpoints
# -------------------------

@router.get("/check-login")
def check_login(current_user: User = Depends(get_current_user)):
    """
    Check if the user is currently logged in.

    Args:
        current_user (User): The authenticated user (auto-injected).

    Returns:
        dict: Message indicating whether the user is logged in.
    """
    # Verify authentication by checking if user object is valid
    if current_user:
        return {"message": "User is logged in"}
    else:
        return {"message": "User is not logged in"}


@router.get("/", response_model=UserResponse)
def get_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve details of the currently logged-in user.

    Args:
        db (Session): SQLAlchemy database session.
        current_user (User): Authenticated user.

    Raises:
        HTTPException: 404 if the user is not found in the database.

    Returns:
        UserResponse: Basic user information (ID, name, email).
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(current_user.id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.patch("/", response_model=UserResponse)
def edit_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user profile information.

    Steps:
    1. Ensure the user is logged in.
    2. Fetch the user record from the database.
    3. Update fields that were provided (name, email, or password).
    4. Commit and refresh the changes.

    Args:
        user_data (UserUpdate): Data fields to update.
        db (Session): Database session.
        current_user (User): Authenticated user.

    Raises:
        HTTPException: 403 if not logged in.
        HTTPException: 404 if user not found.

    Returns:
        UserResponse: Updated user details.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be logged in to edit your profile"
        )

    user_repo = UserRepository(db)
    db_user = user_repo.get_user_by_id(current_user.id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update only provided fields
    if user_data.name:
        db_user.name = user_data.name
    if user_data.email:
        db_user.email = user_data.email
    if user_data.password:
        # Hash the new password before storing it
        db_user.password_hash = get_password_hash(user_data.password)

    db.commit()
    db.refresh(db_user)

    return db_user


@router.delete("/")
def delete_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete the currently authenticated user's account.

    Args:
        db (Session): Database session.
        current_user (User): Authenticated user.

    Raises:
        HTTPException: 403 if not logged in.
        HTTPException: 404 if user not found.

    Returns:
        dict: Confirmation message after successful deletion.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be logged in to delete your profile"
        )

    user_repo = UserRepository(db)
    db_user = user_repo.get_user_by_id(current_user.id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Remove user record permanently
    db.delete(db_user)
    db.commit()

    return {"message": "User deleted successfully"}
