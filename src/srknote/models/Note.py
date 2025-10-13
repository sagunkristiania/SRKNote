
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey,Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from ..config.base import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    user_enc=Column(Boolean,default=False)
    enc_key=Column(Text)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)