
from fastapi import HTTPException, Depends

from ..Schemas.Schemas import UserSchema
from ..models.User import User
from ..repository.BaseRepository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(User, db)

    async def create_user(self, user: UserSchema):
        db_user = User(
            name=user.name,
            email=user.email,
            password_hash=user.password_hash
        )
        self.db.add(db_user)
        self.db.commit()
        return db_user

    async def get_user_by_email(self, email: str):
        return self.db.query(self.model).filter(self.model.email == email).first()

    async def get_user_by_id(self, user_id: int):
        return self.db.query(self.model).filter(self.model.id == user_id).first()

    async def update_user(self, user):
        db_user = self.get_user_by_id(user.id)
        if not db_user:
            raise HTTPException(status_code=404, detail='User Not Found')
        if user.name:
            db_user.name = user.name
        if user.email:
            db_user.email = user.email
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def delete_user(self, user):
        db_user = self.get_user_by_id(user.id)
        if not db_user:
            raise HTTPException(status_code=404, detail='User Not Found')
        self.db.delete(db_user)
        self.db.commit()