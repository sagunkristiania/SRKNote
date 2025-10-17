from ..config.base import Base
import uuid
from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    """
    Represents a registered user in SRKNote.

    Each user has a unique email, a securely hashed password, and a creation timestamp.
    All notes created by this user are linked via a relationship, enabling
    automatic cascading delete when the user is removed.
    """
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for each user"
    )
    name = Column(Text, nullable=False, comment="User's full name")
    email = Column(Text, unique=True, nullable=False, comment="User's email address")
    password_hash = Column(Text, nullable=False, comment="Hashed password for secure authentication")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, comment="Timestamp when the user was created")

    # Relationship to notes: deleting a user deletes all their notes automatically
    notes = relationship(
        "Note",             # Related model
        back_populates="user",
        cascade="all, delete-orphan",  # Ensures notes are deleted with the user
        passive_deletes=True            # Works with database ON DELETE CASCADE
    )
