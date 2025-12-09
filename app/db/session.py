"""
This module handles the database session and engine creation.
It sets up the SQLAlchemy engine to use a shared In-Memory SQLite connection
managed by DBSecurityManager, ensuring strict data security (decryption in RAM).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from app.core.db_security import db_security

# Database URL for In-Memory SQLite
DATABASE_URL = "sqlite://"

# Create engine with StaticPool to share the same in-memory connection across threads
# The connection is created/populated by db_security.get_connection
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    creator=db_security.get_connection
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def reconfigure_engine(new_url: str):
    """
    No-op: The engine is statically configured to use the memory connection from DBSecurityManager.
    """
    pass

def get_db():
    """
    FastAPI dependency that provides a database session for each request.
    
    Ensures proper cleanup:
    - Routes must explicitly call db.commit() for changes
    - Any uncommitted changes are rolled back on close
    - Session is always closed, releasing the connection
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        # Explicit rollback on unhandled exceptions
        db.rollback()
        raise
    finally:
        # Close will also rollback any uncommitted transaction
        db.close()
