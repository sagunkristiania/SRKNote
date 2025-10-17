"""
UserRepository.py
-----------------
Repository for User model in SRKNote.

Handles all database operations related to users:
- Create
- Read (by ID or by email)
- Update
- Delete
"""

from fastapi import HTTPException
from ..Schemas.Schemas import UserSchema
from ..models.User import User
from ..repository.BaseRepository import BaseRepository


class UserRepository(BaseRepository):
    """
    Repository class for performing CRUD operations on User model.

    Inherits from BaseRepository to provide generic database session handling.
    """

    def __init__(self, db):
        """
        Initialize UserRepository with a database session.

        Args:
            db: SQLAlchemy database session.
        """
        super().__init__(User, db)

    def create_user(self, user: UserSchema) -> User:
        """
        Create a new user in the database.

        Args:
            user (UserSchema): User data to insert.

        Returns:
            User: The newly created User object.
        """
        db_user = User(
            name=user.name,
            email=user.email,
            password_hash=user.password_hash
        )
        self.db.add(db_user)
        self.db.commit()
        return db_user

    def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by email address.

        Args:
            email (str): Email of the user to fetch.

        Returns:
            User | None: The User object if found, else None.
        """
        return self.db.query(self.model).filter(self.model.email == email).first()

    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): ID of the user.

        Returns:
            User | None: The User object if found, else None.
        """
        return self.db.query(self.model).filter(self.model.id == user_id).first()

    def update_user(self, user: UserSchema) -> User:
        """
        Update an existing user's details.

        Args:
            user (UserSchema): User data with updated fields.

        Raises:
            HTTPException: 404 if user is not found.

        Returns:
            User: Updated User object.
        """
        db_user = self.get_user_by_id(user.id)
        if not db_user:
            raise HTTPException(status_code=404, detail='User Not Found')
        if user.name:
            db_user.name = user.name
        if user.email:
            db_user.email = user.email
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user: UserSchema):
        """
        Delete a user from the database.

        Args:
            user (UserSchema): User object to delete.

        Raises:
            HTTPException: 404 if user is not found.

        Returns:
            None
        """
        db_user = self.get_user_by_id(user.id)
        if not db_user:
            raise HTTPException(status_code=404, detail='User Not Found')
        self.db.delete(db_user)
        self.db.commit()
