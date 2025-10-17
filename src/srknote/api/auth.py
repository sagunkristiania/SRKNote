"""
auth.py
---------
This module handles user authentication and registration functionalities for the SRKNote API.

It provides:
- User registration endpoint (`/register`)
- User login endpoint (`/login`)
- User logout endpoint (`/logout`)

It uses FastAPI’s dependency injection for database sessions and security utilities for
password hashing, verification, and JWT token generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from ..config.db import get_db
from ..config.security import (
    verify_password,
    hash_password as get_password_hash,
    create_access_token,
    get_current_user,
)
from ..repository.UserRepository import UserRepository
from ..Schemas.Schemas import UserSchema, UserRegister, Token

# Create a router instance for all authentication-related routes
router = APIRouter(prefix="/api/v1/users", tags=["Authentication"])

# Define the OAuth2 scheme to handle bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

# Dependency for injecting database session into routes
db = Depends(get_db)


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.

    Steps:
    1. Check if a user with the given email already exists.
    2. Hash the provided password for secure storage.
    3. Create a new user record in the database.
    4. Return a success message and basic user details.

    Args:
        user_data (UserRegister): The registration data (name, email, password).
        db (Session): SQLAlchemy session dependency.

    Raises:
        HTTPException: 409 if a user with the same email already exists.

    Returns:
        dict: Success message with the newly created user's details.
    """
    user_repo = UserRepository(db)

    # Check for existing user by email
    existing_user = user_repo.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    # Securely hash the user's password before saving
    hashed_password = get_password_hash(user_data.password)

    # Prepare a schema object for user creation
    user_schema = UserSchema(
        id=0,
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password
    )

    # Create the new user record
    new_user = user_repo.create_user(user_schema)

    # Return confirmation response
    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user and issue an access token.

    Steps:
    1. Retrieve the user by their email (username field).
    2. Verify the password using the stored password hash.
    3. Generate and return a JWT access token upon successful authentication.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data containing username (email) and password.
        db (Session): SQLAlchemy session dependency.

    Raises:
        HTTPException: 401 if credentials are invalid.

    Returns:
        dict: A JWT access token and its type ("bearer").
    """
    user_repo = UserRepository(db)

    # Attempt to find user by email
    user = user_repo.get_user_by_email(form_data.username)

    # Validate user existence and password correctness
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token (JWT) embedding user ID and email
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    # Return token response
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(token: str = Depends(get_current_user)):
    """
    Log the user out.

    Since JWTs are stateless, this endpoint serves as an acknowledgment.
    The user should delete or invalidate their token on the client side.

    Args:
        token (str): The JWT token from the authenticated user (validated automatically).

    Returns:
        dict: Confirmation message for logout.
    """
    # Inform the client to discard their stored token
    return {"message": "Logout successful. Please delete your token."}
