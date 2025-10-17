"""
db.py
------
Database configuration module for SRKNote.

This module manages PostgreSQL connection setup, SQLAlchemy engine creation,
and session handling. It ensures consistent and efficient database access
throughout the SRKNote application.
"""

import os
from .config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def get_db_url() -> str:
    """
    Build and return the PostgreSQL database URL for SRKNote.

    The URL is constructed dynamically using environment variables
    (for containerized environments) or configuration values
    from the `settings` object.

    Returns:
        str: PostgreSQL connection string.
    """
    user = os.getenv('POSTGRES_USER', settings.DB_USER)
    password = os.getenv('POSTGRES_PASSWORD', settings.DB_PASSWORD.get_secret_value())
    host = os.getenv('POSTGRES_HOST', settings.DB_HOST)
    db = os.getenv('POSTGRES_DB', settings.DB_NAME)
    port = os.getenv('POSTGRES_PORT_IN_DOCKER', str(settings.DB_PORT))

    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def get_engine():
    """
    Initialize and return the SQLAlchemy engine for SRKNote.

    Uses a singleton pattern to prevent redundant engine creation
    during the application’s lifecycle.
    """
    global _engine
    if '_engine' not in globals():
        _engine = create_engine(get_db_url())
    return _engine


# Base class for all SRKNote ORM models
Base = declarative_base()


def get_session_local():
    """
    Create and return a SQLAlchemy session factory bound to the SRKNote engine.

    Returns:
        sessionmaker: Configured session factory instance.
    """
    return sessionmaker(bind=get_engine())


def get_db():
    """
    Database session dependency for SRKNote routes.

    Yields a new database session for each API request and ensures
    the session is properly closed afterward — even on errors.

    Example:
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
