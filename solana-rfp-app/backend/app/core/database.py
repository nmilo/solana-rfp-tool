from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from app.core.config import settings

# For development, use SQLite if no DATABASE_URL is provided
database_url = settings.DATABASE_URL or os.getenv("DATABASE_URL")
if database_url:
    print(f"Using database URL: {database_url[:50]}...")
    engine = create_engine(database_url)
else:
    print("No DATABASE_URL found, using SQLite fallback")
    # Fallback to SQLite for development
    engine = create_engine("sqlite:///./solana_rfp.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import Base from models to ensure tables are defined
from app.models.database import Base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
