"""
Database connection setup using SQLAlchemy.
Uses SQLite for simplicity. Can be swapped with PostgreSQL or MySQL easily.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# SQLite database file stored locally
DATABASE_URL = "sqlite:///./gym_tracker.db"

# Create the engine (connect_args is needed only for SQLite)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal is used to create individual database sessions per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Creates all database tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency function that provides a database session per request.
    Automatically closes the session when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
