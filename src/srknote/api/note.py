"""
note.py
--------
This module defines all endpoints related to creating, reading, updating, and deleting
notes for authenticated users.

Feature:
- Create notes (with optional user-level encryption)
- Retrieve all notes belonging to a user
- Access (decrypt) a specific note
- Edit existing notes securely
- Delete notes

Each route enforces user authorization and optional encryption/decryption
based on user-provided or global encryption keys.
"""

from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..Schemas.Schemas import (
    NoteSchema,
    CreateNoteSchema,
    EncryptRequest,
    NoteResponse,
    NoteUpdate,
    DecryptRequest,
)
from ..config.config import settings
from ..config.db import get_db
from ..config.security import (
    get_current_user,
    encrypt_data,
    hash_context,
    encrypt_key,
    verify_key,
    decrypt_data,
)
from ..repository.NoteRepository import NoteRepository
from ..models.User import User

# Define the router for all note-related endpoints
router = APIRouter(prefix="/api/v1/notes", tags=["Notes"])


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def add_note(
    note_data: CreateNoteSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new encrypted or non-encrypted note.

    Steps:
    1. Verify user authentication.
    2. If user-level encryption is enabled, require an encryption password.
    3. Encrypt title and content using either:
       - User-provided encryption key (if `user_enc` is True)
       - Default system key (from settings)
    4. Store the note in the database.

    Args:
        note_data (CreateNoteSchema): Data required to create a note.
        db (Session): SQLAlchemy database session.
        current_user (User): The authenticated user creating the note.

    Raises:
        HTTPException: 403 if user is unauthenticated.
        HTTPException: 400 if encryption is enabled but no key is provided.

    Returns:
        NoteResponse: The newly created note.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be logged in to create a note"
        )

    # Ensure encryption password is provided if user-level encryption is chosen
    if note_data.user_enc and not note_data.enc_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide Encryption Password to encrypt the note"
        )

    note_repo = NoteRepository(db)

    # Determine encryption key (user or global)
    enc_key = settings.ENC_KEY
    if note_data.user_enc:
        enc_key = note_data.enc_key

    # Encrypt and hash the encryption key
    key = encrypt_key(enc_key)
    hash_contxt = hash_context()
    hashed_enc_key = hash_contxt.hash(enc_key)

    # Prepare encryption requests for both title and content
    content = EncryptRequest(data=note_data.content, key=key)
    title = EncryptRequest(data=note_data.title, key=key)

    # Perform encryption
    encrypted_content = encrypt_data(content)
    encrypted_title = encrypt_data(title)

    # Construct schema for DB insertion
    db_note = NoteSchema(
        title=encrypted_title,
        content=encrypted_content,
        user_id=current_user.id,
        user_enc=note_data.user_enc,
        enc_key=hashed_enc_key
    )

    # Store the encrypted note in the DB
    new_db_note = note_repo.create_note(db_note)

    return new_db_note


@router.get("/", response_model=List[NoteResponse])
def list_all_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all notes belonging to the authenticated user.

    Args:
        db (Session): Database session.
        current_user (User): Authenticated user.

    Returns:
        List[NoteResponse]: All notes owned by the current user.
    """
    note_repo = NoteRepository(db)
    notes = note_repo.get_note_by_user_id(current_user.id)
    return notes if notes else []


@router.post("/{note_id}", response_model=NoteResponse)
def access_note(
    note_id: int,
    enc_key: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Access and decrypt a specific note.

    Steps:
    1. Fetch the note by its ID.
    2. Verify that the current user owns the note.
    3. Validate the encryption key.
    4. Decrypt the title and content for the response.

    Args:
        note_id (int): ID of the note to access.
        enc_key (Optional[str]): User-provided encryption key (if applicable).
        db (Session): Database session.
        current_user (User): Authenticated user.

    Raises:
        HTTPException: 404 if note not found.
        HTTPException: 403 if user unauthorized or key invalid.

    Returns:
        NoteResponse: Decrypted note details.
    """
    note_repo = NoteRepository(db)
    note = note_repo.get_note_by_id(note_id)

    # Validate note existence
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # Ensure the note belongs to the current user
    if note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this note"
        )

    # Use system encryption key if user encryption is disabled
    if not note.user_enc:
        enc_key = settings.ENC_KEY

    # Encrypt provided key for decryption use
    key = encrypt_key(enc_key)

    # Verify the provided encryption key matches stored hash
    if not verify_key(enc_key, note.enc_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid key"
        )

    # Decrypt both title and content
    decrypt_title_request = DecryptRequest(encrypted_data=note.title, key=key)
    decrypted_title = decrypt_data(decrypt_title_request)

    decrypt_content_request = DecryptRequest(encrypted_data=note.content, key=key)
    decrypted_content = decrypt_data(decrypt_content_request)

    # Prepare response with decrypted data
    response = NoteResponse(
        id=note.id,
        title=decrypted_title,
        content=decrypted_content,
        user_id=note.user_id,
    )
    return response


@router.patch("/{note_id}", response_model=NoteResponse)
def edit_note(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Edit an existing note's title or content.

    Steps:
    1. Validate note existence and ownership.
    2. Verify encryption key.
    3. Encrypt updated fields and save changes.

    Args:
        note_id (int): The ID of the note to update.
        note_data (NoteUpdate): Fields to update.
        db (Session): Database session.
        current_user (User): Authenticated user.

    Raises:
        HTTPException: 404 if note not found.
        HTTPException: 403 if unauthorized or invalid key.

    Returns:
        NoteResponse: Updated and encrypted note.
    """
    note_repo = NoteRepository(db)
    db_note = note_repo.get_note_by_id(note_id)

    # Validate note existence
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # Ensure user owns the note
    if db_note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this note"
        )

    # Determine encryption key
    enc_key = settings.ENC_KEY
    if db_note.user_enc:
        enc_key = note_data.enc_key

    key = encrypt_key(enc_key)

    # Verify encryption key validity
    if not verify_key(enc_key, db_note.enc_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid key"
        )

    # Encrypt updated title and content
    content = EncryptRequest(data=note_data.content, key=key)
    title = EncryptRequest(data=note_data.title, key=key)

    encrypted_content = encrypt_data(content)
    encrypted_title = encrypt_data(title)

    # Update only provided fields
    if note_data.title:
        db_note.title = encrypted_title
    if note_data.content:
        db_note.content = encrypted_content

    db.commit()
    db.refresh(db_note)

    return db_note


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific note.

    Args:
        note_id (int): ID of the note to delete.
        db (Session): Database session.
        current_user (User): Authenticated user.

    Raises:
        HTTPException: 404 if note not found.
        HTTPException: 403 if user not authorized.

    Returns:
        dict: Confirmation message.
    """
    note_repo = NoteRepository(db)
    db_note = note_repo.get_note_by_id(note_id)

    # Ensure note exists
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # Ensure note belongs to the current user
    if db_note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this note"
        )

    # Delete and commit the note removal
    db.delete(db_note)
    db.commit()

    return {"message": "Note deleted successfully"}
