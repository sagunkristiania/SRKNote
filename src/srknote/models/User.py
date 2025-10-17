from ..config.base import Base
import uuid
from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class User(Base):
    """
    Represents a registered user in SRKNote.

    Each user has a unique email, a secure hashed password, and a creation timestamp.
    Notes created by this user are linked via foreign key in the Note model.
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
