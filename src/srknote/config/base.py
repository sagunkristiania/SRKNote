"""
base.py
---------
Defines the SQLAlchemy declarative base class used across all ORM models.
This serves as the foundation for creating and mapping database tables.
"""

from sqlalchemy.orm import declarative_base

# Create a base class for all SQLAlchemy ORM models.
# All model classes will inherit from this Base to define database tables.
Base = declarative_base()
