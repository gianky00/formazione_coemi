"""
This module handles the database session and engine creation.
It reads the database URL from the environment variables and sets up the
SQLAlchemy engine and session factory. It also provides a dependency
for FastAPI to get a database session.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Default URL (will be overwritten by DBSecurityManager in main.py)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database_documenti.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def reconfigure_engine(new_url: str):
    """
    Replaces the global engine with a new one pointing to the specific (temp) file.
    Updates SessionLocal binding.
    """
    global engine, SessionLocal, DATABASE_URL

    # Dispose old engine connections
    engine.dispose()

    DATABASE_URL = new_url
    # Create new engine
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

    # Update session factory
    SessionLocal.configure(bind=engine)

def get_db():
    """
    FastAPI dependency that provides a database session for each request.
    It ensures that the database session is always closed after the request
    is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
