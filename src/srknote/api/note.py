import pdb
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..Schemas.Schemas import NoteSchema, CreateNoteSchema, EncryptRequest, NoteResponse, NoteUpdate, DecryptRequest
from ..config.config import settings
from ..config.db import get_db
from ..config.security import get_current_user, encrypt_data, hash_context, encrypt_key, verify_key, decrypt_data
from ..repository.NoteRepository import NoteRepository
from ..models.User import User

router = APIRouter(prefix="/api/v1/notes", tags=["Notes"])


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def add_note(
        note_data: CreateNoteSchema,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be logged in to create a note"
        )

    if note_data.user_enc and not note_data.enc_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide Encryption Passsword to encrypt the note"
        )
    note_repo = NoteRepository(db)

    enc_key = settings.ENC_KEY
    if note_data.user_enc:
        enc_key = note_data.enc_key

    key = encrypt_key(enc_key)

    hash_contxt = hash_context()

    hashed_enc_key = hash_contxt.hash(enc_key)

    content = EncryptRequest(data=note_data.content, key=key)

    title = EncryptRequest(data=note_data.title, key=key)

    encrypted_content = encrypt_data(content)

    encrypted_title = encrypt_data(title)

    db_note = NoteSchema(
        title=encrypted_title,
        content=encrypted_content,
        user_id=current_user.id,
        user_enc=note_data.user_enc,
        enc_key=hashed_enc_key
    )

    new_db_note = note_repo.create_note(db_note)

    return new_db_note


@router.get("/", response_model=List[NoteResponse])
def list_all_notes(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
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
    note_repo = NoteRepository(db)

    note = note_repo.get_note_by_id(note_id)

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    if note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this note"
        )

    if not note.user_enc:
        enc_key = settings.ENC_KEY

    key = encrypt_key(enc_key)

    if not verify_key(enc_key, note.enc_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid key"
        )

    decrypt_title_request = DecryptRequest(encrypted_data=note.title, key=key)
    decrypted_title = decrypt_data(decrypt_title_request)
    decrypt_content_request = DecryptRequest(encrypted_data=note.content, key=key)
    decrypted_content = decrypt_data(decrypt_content_request)

    response = NoteResponse(
        id=note.id,
        title=decrypted_title,
        content=decrypted_content,
        user_id=note.user_id,
    )
    return response


@router.put("/{note_id}", response_model=NoteResponse)
def edit_note(
        note_id: int,
        note_data: NoteUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    note_repo = NoteRepository(db)

    db_note = note_repo.get_note_by_id(note_id)

    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    if db_note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this note"
        )

    enc_key = settings.ENC_KEY

    if db_note.user_enc:
        enc_key = note_data.enc_key

    key = encrypt_key(enc_key)

    if not verify_key(enc_key, db_note.enc_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid key"
        )

    content = EncryptRequest(data=note_data.content, key=key)

    title = EncryptRequest(data=note_data.title, key=key)

    encrypted_content = encrypt_data(content)

    encrypted_title = encrypt_data(title)

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
    note_repo = NoteRepository(db)
    db_note = note_repo.get_note_by_id(note_id)

    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    if db_note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this note"
        )

    db.delete(db_note)
    db.commit()

    return {"message": "Note deleted successfully"}
