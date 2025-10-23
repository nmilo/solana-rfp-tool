from sqlalchemy import Column, String, Text, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
import json

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)
    login_count = Column(String, default="0")  # Store as string for simplicity
    
    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.name}')>"

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    tags = Column(Text, default="[]")  # JSON string for SQLite compatibility
    category = Column(String(100))
    confidence_threshold = Column(Float, default=0.1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100), default="admin")
    last_modified_by = Column(String(100), default="admin")
    
    def get_tags(self):
        """Get tags as a list"""
        try:
            return json.loads(self.tags) if self.tags else []
        except:
            return []
    
    def set_tags(self, tags_list):
        """Set tags from a list"""
        self.tags = json.dumps(tags_list) if tags_list else "[]"

class QuestionSubmission(Base):
    __tablename__ = "question_submissions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    input_type = Column(String(20), nullable=False)  # 'text' or 'pdf'
    raw_input = Column(Text)
    extracted_questions = Column(Text)  # JSON string
    matched_answers = Column(Text)  # JSON string
    confidence_scores = Column(Text)  # JSON string
    processing_status = Column(String(50), default="pending")
    created_at = Column(DateTime, server_default=func.now())
