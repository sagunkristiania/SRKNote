"""
BaseRepository.py
-----------------
Generic repository for SRKNote.

Provides basic CRUD operations for any SQLAlchemy model. This
class serves as a base for specialized repositories like
UserRepository or NoteRepository.
"""

from ..config.base import Base


class BaseRepository:
    """
    Base repository class for SRKNote database models.

    Attributes:
        model (Base): SQLAlchemy model class (e.g., User, Note).
        db: SQLAlchemy session for database operations.
    """

    def __init__(self, model, db):
        """
        Initialize a new BaseRepository.

        Args:
            model (Base): SQLAlchemy ORM model class.
            db: SQLAlchemy database session.
        """
        self.db = db
        self.model = model
