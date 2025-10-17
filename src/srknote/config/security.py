"""
security.py
-------------
Security module for SRKNote.

This module handles all aspects of:
- Password hashing and verification
- JWT token creation and decoding
- Encryption and decryption of note content
- Encryption key management for user-level encryption

It ensures that SRKNote data is securely stored and transmitted,
and that only authenticated users can access their notes.
"""

import hashlib
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from cryptography.fernet import Fernet, InvalidToken
import base64

from ..Schemas.Schemas import EncryptRequest, DecryptRequest
from ..config.db import get_db
from ..models.User import User
from .config import settings
from pydantic import SecretStr
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer


# -------------------------
# Hashing Utilities
# -------------------------
def hash_context() -> CryptContext:
    """
    Returns a CryptContext configured for hashing passwords.

    Uses multiple secure schemes (bcrypt, pbkdf2_sha256, argon2)
    to provide flexibility and compatibility.

    Raises:
        HTTPException: 500 if context creation fails.
    """
    try:
        return CryptContext(schemes=["bcrypt", "pbkdf2_sha256", "argon2"], deprecated="auto")
    except Exception:
        raise HTTPException(status_code=500, detail="Hash context creation failed")


def hash_password(password: SecretStr) -> str:
    """
    Hash a plaintext password for storage.

    Args:
        password (SecretStr): Plaintext password.

    Returns:
        str: Hashed password ready for storage.
    """
    pwd_context = hash_context()
    return pwd_context.hash(password.get_secret_value())


def verify_password(plain_password: SecretStr, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its hashed version.

    Args:
        plain_password (SecretStr): User-supplied password.
        hashed_password (str): Stored hashed password.

    Returns:
        bool: True if password matches, False otherwise.
    """
    pwd_context = hash_context()
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------
# JWT Token Utilities
# -------------------------
def create_access_token(data: dict) -> str:
    """
    Create a JWT access token for authenticated SRKNote users.

    Args:
        data (dict): Data to include in the token (e.g., user id, email).

    Returns:
        str: Encoded JWT token.
    """
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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def decode_access_token(token: str = Depends(oauth2_scheme), db=Depends(get_db)) -> dict:
    """
    Decode a JWT token and return the payload.

    Verifies that the token belongs to a valid SRKNote user.

    Args:
        token (str): JWT token from the Authorization header.
        db: Database session dependency.

    Raises:
        HTTPException: 401 for invalid or missing token/email.

    Returns:
        dict: JWT payload.
    """
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
    """
    Retrieve the currently authenticated SRKNote user from the JWT token.

    Args:
        token (str): JWT token from the Authorization header.
        db: Database session dependency.

    Raises:
        HTTPException: 401 if token is invalid or user does not exist.

    Returns:
        User: SQLAlchemy User object corresponding to the token.
    """
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


# -------------------------
# Encryption Utilities
# -------------------------
def encrypt_data(request: EncryptRequest) -> str:
    """
    Encrypt note content using Fernet symmetric encryption.

    Args:
        request (EncryptRequest): Contains data to encrypt and encryption key.

    Raises:
        HTTPException: 400 for missing/invalid key or data, 500 for encryption errors.

    Returns:
        str: Base64-encoded encrypted string.
    """
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="Data cannot be empty")
        if not request.key:
            raise HTTPException(status_code=400, detail="Key cannot be empty")

        try:
            key_bytes = request.key.encode('utf-8')
            decoded = base64.urlsafe_b64decode(key_bytes)
            if len(decoded) != 32:
                raise ValueError("Invalid key length")
        except Exception:
            raise HTTPException(status_code=400,
                                detail="Invalid key format. Key must be 32 url-safe base64-encoded bytes")

        fernet = Fernet(key_bytes)
        encrypted_data = fernet.encrypt(request.data.encode('utf-8'))
        return encrypted_data.decode('utf-8')

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Encryption failed")


def decrypt_data(request: DecryptRequest) -> str:
    """
    Decrypt note content using Fernet symmetric encryption.

    Args:
        request (DecryptRequest): Contains encrypted data and decryption key.

    Raises:
        HTTPException: 400 for missing/invalid key or data, 500 for decryption errors.

    Returns:
        str: Decrypted plaintext string.
    """
    try:
        if not request.encrypted_data:
            raise HTTPException(status_code=400, detail="Encrypted data cannot be empty")
        if not request.key:
            raise HTTPException(status_code=400, detail="Key cannot be empty")

        try:
            key_bytes = request.key.encode('utf-8')
            decoded = base64.urlsafe_b64decode(key_bytes)
            if len(decoded) != 32:
                raise ValueError("Invalid key length")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid key format")

        fernet = Fernet(key_bytes)

        try:
            decrypted_data = fernet.decrypt(request.encrypted_data.encode('utf-8'))
        except InvalidToken:
            raise HTTPException(status_code=400, detail="Invalid encrypted data or wrong key")

        return decrypted_data.decode('utf-8')

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")


def encrypt_key(key: str) -> str:
    """
    Convert a plaintext key into a base64-encoded 32-byte key for Fernet encryption.

    Args:
        key (str): Plaintext key.

    Raises:
        HTTPException: 500 if encryption fails.

    Returns:
        str: Base64-encoded key string.
    """
    try:
        key_bytes = hashlib.sha256(key.encode()).digest()
        return base64.urlsafe_b64encode(key_bytes).decode()
    except Exception:
        raise HTTPException(status_code=500, detail="Encryption failed")


def verify_key(key, hashed_key: str) -> bool:
    """
    Verify a plaintext key against its hashed version using passlib.

    Args:
        key (str): Plaintext key.
        hashed_key (str): Stored hashed key.

    Returns:
        bool: True if keys match, False otherwise.
    """
    pwd_context = hash_context()
    return pwd_context.verify(key, hashed_key)
