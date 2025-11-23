"""
This module handles the database session and engine creation.
It sets up the SQLAlchemy engine to use a shared In-Memory SQLite connection
managed by DBSecurityManager, ensuring strict data security (decryption in RAM).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv
from app.core.db_security import db_security

load_dotenv()

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
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
