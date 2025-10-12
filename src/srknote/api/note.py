from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from ..config.db import get_db
from ..config.security import get_current_user
from ..repository.NoteRepository import NoteRepository
from ..models.Note import Note
from ..models.User import User

router = APIRouter(prefix="/api/notes", tags=["Notes"])


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def add_note(
        note_data: NoteCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Create a new note"""
    note_repo = NoteRepository(db)

    db_note = Note(
        title=note_data.title,
        content=note_data.content,
        user_id=current_user.id
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return db_note


@router.get("/", response_model=List[NoteResponse])
async def list_all_notes(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get all notes for the current user"""
    note_repo = NoteRepository(db)
    notes = await note_repo.get_note_by_user_id(current_user.id)
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
async def access_note(
        note_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get a specific note by ID"""
    note_repo = NoteRepository(db)
    note = await note_repo.get_note_by_id(note_id)

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # Check if note belongs to current user
    if note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this note"
        )

    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def edit_note(
        note_id: int,
        note_data: NoteUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Update a note"""
    note_repo = NoteRepository(db)
    db_note = await note_repo.get_note_by_id(note_id)

    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # Check if note belongs to current user
    if db_note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this note"
        )

    # Update note fields
    if note_data.title:
        db_note.title = note_data.title
    if note_data.content:
        db_note.content = note_data.content

    db.commit()
    db.refresh(db_note)

    return db_note


@router.delete("/{note_id}")
async def delete_note(
        note_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Delete a note"""
    note_repo = NoteRepository(db)
    db_note = await note_repo.get_note_by_id(note_id)

    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # Check if note belongs to current user
    if db_note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this note"
        )

    db.delete(db_note)
    db.commit()

    return {"message": "Note deleted successfully"}