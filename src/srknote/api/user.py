from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, SecretStr
from typing import List, Optional

from ..config.db import get_db
from ..config.security import get_current_user, hash_password as get_password_hash
from ..repository.UserRepository import UserRepository
from ..models.User import User

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[SecretStr] = None


@router.get("/check-login")
def check_login(current_user: User = Depends(get_current_user)):
    if User:
        return {"message": "User is logged in"}
    else:
        return {"message": "User is not logged in"}

@router.get("/", response_model=List[UserResponse])
def get_all_users(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # user_repo = UserRepository(db)
    users = db.query(User).all()
    return users


@router.get("/", response_model=UserResponse)
def get_user(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
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

    if user_data.name:
        db_user.name = user_data.name
    if user_data.email:
        db_user.email = user_data.email
    if user_data.password:
        db_user.password_hash = get_password_hash(user_data.password)

    db.commit()
    db.refresh(db_user)

    return db_user


@router.delete("/")
def delete_user(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
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

    db.delete(db_user)
    db.commit()

    return {"message": "User deleted successfully"}
