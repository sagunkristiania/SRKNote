from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from ..config.base import Base

class Note(Base):
    """
    Represents a secure note in SRKNote.

    Notes can be encrypted using either a default key or a user-provided key.
    Deleting a user automatically deletes all their notes via ON DELETE CASCADE.

    Attributes:
        id: Unique auto-incremented note ID
        title: Encrypted title of the note
        content: Encrypted content of the note
        user_id: Owner user ID (foreign key with cascade delete)
        user_enc: Whether the note uses a user-specific encryption key
        enc_key: Hashed encryption key if user-specific encryption is used
        created_at: Note creation timestamp
        updated_at: Timestamp of the last note update
    """
    __tablename__ = "notes"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Auto-incremented note ID"
    )
    title = Column(
        Text,
        nullable=False,
        comment="Encrypted title of the note"
    )
    content = Column(
        Text,
        nullable=False,
        comment="Encrypted content of the note"
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Owner user ID; deleting the user deletes this note automatically"
    )
    user_enc = Column(
        Boolean,
        default=False,
        comment="Indicates if note uses user-specific encryption key"
    )
    enc_key = Column(
        Text,
        comment="Hashed encryption key if user-specific encryption is used"
    )
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        comment="Timestamp when note was created"
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Last update timestamp"
    )

    # Relationship to the user; enables ORM-level cascade deletes
    user = relationship(
        "User",
        back_populates="notes",
        passive_deletes=True  # Works with ON DELETE CASCADE
    )
