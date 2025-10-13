
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, SecretStr
from uuid import UUID

class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    def strong_password(cls, v):
        if len(v) < 8 or not any(c.isdigit() for c in v) or not any(c.isupper() for c in v):
            raise ValueError("Password must be at least 8 characters, include a number and an uppercase letter")
        return v

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr

class UserSchema(BaseModel):
    id:int
    name:str
    email:EmailStr
    password_hash:str


class NoteIn(BaseModel):
    title: str
    content: str
    user_enc:bool

class NoteSchema(BaseModel):
    id: Optional[int]=None
    user_id: UUID
    title: str
    content: str
    user_enc:bool
    enc_key:str

class CreateNoteSchema(BaseModel):
    title: str
    content: str
    user_enc:bool
    enc_key:Optional[str] = None


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    enc_key: Optional[str] = None

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: SecretStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class EncryptRequest(BaseModel):
    key: str
    data: str


class DecryptRequest(BaseModel):
    key: str
    encrypted_data: str



class NoteCreate(BaseModel):
    title: str
    content: str



class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: UUID