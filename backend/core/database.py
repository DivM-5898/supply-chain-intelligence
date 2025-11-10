"""
Database Connection Module
PostgreSQL database setup (optional for Render deployment)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional
import os

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/supplier_db"
)

# For development, use SQLite if PostgreSQL not available
if DATABASE_URL.startswith("postgresql"):
    try:
        engine = create_engine(DATABASE_URL)
        Base = declarative_base()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}. Using in-memory storage.")
        engine = None
        Base = None
        SessionLocal = None
else:
    engine = None
    Base = None
    SessionLocal = None


def get_db():
    """Get database session"""
    if SessionLocal is None:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

