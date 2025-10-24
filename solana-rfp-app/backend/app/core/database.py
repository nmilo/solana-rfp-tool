from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# For development, use SQLite if no DATABASE_URL is provided
if settings.DATABASE_URL:
    engine = create_engine(settings.DATABASE_URL)
else:
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
