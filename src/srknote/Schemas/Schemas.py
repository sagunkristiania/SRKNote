"""
Schemas.py
----------
Pydantic models for SRKNote API requests and responses.

These schemas handle data validation and serialization for:
- User registration and login
- Token management
- Notes creation, retrieval, encryption/decryption
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, SecretStr
from uuid import UUID


# ---------------------------
# User-related Schemas
# ---------------------------

class RegisterIn(BaseModel):
    """Input schema for user registration."""
    name: str
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginIn(BaseModel):
    """Input schema for user login."""
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    """Output schema for JWT tokens."""
    access_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    """Output schema for user details."""
    id: UUID
    name: str
    email: EmailStr


class UserSchema(BaseModel):
    """Internal representation of user data for database operations."""
    id: int
    name: str
    email: EmailStr
    password_hash: str


class UserRegister(BaseModel):
    """Schema for creating a new user via API."""
    name: str = Field(..., max_length=50)
    email: EmailStr
    password: SecretStr = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Schema for logging in a user via API."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema representing access token response."""
    access_token: str
    token_type: str


# ---------------------------
# Note-related Schemas
# ---------------------------

class NoteIn(BaseModel):
    """Input schema for note creation."""
    title: str
    content: str
    user_enc: bool  # Indicates if the note should be encrypted using a user key


class NoteSchema(BaseModel):
    """Internal representation of a note for database operations."""
    id: Optional[int] = None
    user_id: UUID
    title: str
    content: str
    user_enc: bool
    enc_key: str  # Hashed encryption key if user encryption is enabled


class CreateNoteSchema(BaseModel):
    """Input schema for creating a new note via API."""
    title: str
    content: str
    user_enc: bool = False
    enc_key: Optional[str] = Field(None, min_length=8)


class NoteUpdate(BaseModel):
    """Schema for updating an existing note."""
    title: Optional[str] = None
    content: Optional[str] = None
    enc_key: Optional[str] = None


class NoteCreate(BaseModel):
    """Alternate input schema for creating a note with max lengths."""
    title: str = Field(..., max_length=50)
    content: str = Field(..., max_length=5000)


class NoteResponse(BaseModel):
    """Output schema for returning note details via API."""
    id: int
    title: str
    content: str
    user_id: UUID


# ---------------------------
# Encryption-related Schemas
# ---------------------------

class EncryptRequest(BaseModel):
    """Request schema for encrypting data."""
    key: str
    data: str


class DecryptRequest(BaseModel):
    """Request schema for decrypting data."""
    key: str
    encrypted_data: str
