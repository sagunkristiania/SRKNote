
import os
from .config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



# Postgres engine

def get_db_url() -> str:
    user = os.getenv('POSTGRES_USER', settings.DB_USER)
    password = os.getenv('POSTGRES_PASSWORD', settings.DB_PASSWORD.get_secret_value())
    host = os.getenv('POSTGRES_HOST', settings.DB_HOST)
    db = os.getenv('POSTGRES_DB', settings.DB_NAME)
    port = os.getenv('POSTGRES_PORT_IN_DOCKER', str(settings.DB_PORT))

    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return url


def get_engine():
    global _engine
    if '_engine' not in globals():
        _engine = create_engine(get_db_url())
    return _engine


Base = declarative_base()


def get_session_local():
    """Get SessionLocal bound to the current engine"""
    return sessionmaker(bind=get_engine())


# print("Database connection is successful!")

def get_db():

    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()