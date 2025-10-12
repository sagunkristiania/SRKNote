
from fastapi import HTTPException

from ..Schemas.Schemas import NoteSchema
from ..models.Note import Note
from ..repository.BaseRepository import BaseRepository


# CREATE USER

class NoteRepository(BaseRepository):

    def __init__(self, db):
        super().__init__(Note, db)

    async def create_note(self, note: NoteSchema):
        db_note = Note(
            title=note.title,
            content=note.content,
            user_id=note.user_id
        )
        new_note=self.db.add(db_note)
        self.db.commit()
        return new_note


    async def get_note_by_id(self, note_id: int):
        return self.db.query(self.model).filter(self.model.id==id).first()

    async def get_note_by_user_id(self, user_id: int):
        return self.db.query(self.model).filter(self.model.user_id == user_id).first()

    async def update_note(self,note):
        db_note=self.get_note_by_id(note.id)
        if not db_note:
            raise HTTPException(detail='Note Not Found')
        if note.title:
            db_note.title=note.title
        if db_note.content:
            db_note.content=note.content
        self.db.commit()
        return self.db.refresh(db_note)

    async def delete_user(self, note):
        db_note=self.get_note_by_id(note.id)
        if not db_note:
            raise HTTPException(detail='Note Not Found')
        return self.db.delete(db_note)



