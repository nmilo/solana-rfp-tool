import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.models.database import User
from app.schemas.auth import UserCreate, UserResponse
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def is_allowed_email(self, email: str) -> bool:
        """Check if email is allowed to access the application"""
        allowed_domains = ["@solana.org"]
        developer_email = "mandicnikola1989@gmail.com"
        
        # Check if it's the developer email
        if email.lower() == developer_email.lower():
            return True
            
        # Check if it's a @solana.org email
        for domain in allowed_domains:
            if email.lower().endswith(domain.lower()):
                return True
                
        return False

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email.lower()).first()
    
    def create_user(self, email: str, name: str = None) -> User:
        """Create a new user"""
        admin_emails = ["mandicnikola1989@gmail.com", "dragan.zurzin@solana.org"]
        is_admin = email.lower() in admin_emails
        user = User(
            email=email.lower(),
            name=name if name else email.split('@')[0],
            is_admin=is_admin
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


    def authenticate_user(self, email: str) -> Optional[User]:
        """Authenticate user by email"""
        # Check if email is allowed
        if not self.is_allowed_email(email):
            return None
            
        user = self.get_user_by_email(email)
        if not user:
            # Auto-create user if they don't exist but email is allowed
            user_data = UserCreate(email=email)
            user = self.create_user(user_data)
        
        # Update login statistics
        user.last_login = datetime.utcnow()
        user.login_count = str(int(user.login_count or "0") + 1)
        self.db.commit()
        
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return email"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
            return email
        except JWTError:
            return None

    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token"""
        email = self.verify_token(token)
        if email is None:
            return None
        return self.get_user_by_email(email)
    
