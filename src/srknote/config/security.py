from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from rest_framework import status

from ..config.db import get_db
from ..models.User import User
from .config import settings
from pydantic import SecretStr
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Header
from fastapi.security.oauth2 import OAuth2PasswordBearer


def hash_context() -> CryptContext:
    return CryptContext(schemes=["bcrypt", "pbkdf2_sha256", "argon2"], deprecated="auto")


def hash_password(password: SecretStr) -> str:
    pwd_context = hash_context()
    return pwd_context.hash(password.get_secret_value())


def verify_password(plain_password: SecretStr, hashed_password: str) -> bool:
    pwd_context = hash_context()
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    data_to_encode = data.copy()
    expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire_time = datetime.now(timezone.utc) + expire
    data_to_encode.update({"exp": expire_time.timestamp()})
    encoded_jwt = jwt.encode(
        data_to_encode,
        settings.JWT_SECRET.get_secret_value(),
        algorithm=settings.JWT_ALG
    )
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def decode_access_token(token: str = Depends(oauth2_scheme), db=Depends(get_db)) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET.get_secret_value(), algorithms=[settings.JWT_ALG])
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail='Invalid Email')
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail='Token Missing')
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid Token')

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET.get_secret_value(), algorithms=[settings.JWT_ALG])
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail='Invalid Email')
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail='Token Missing')
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid Token')
