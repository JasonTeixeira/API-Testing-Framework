"""
User Models - Database and Pydantic schemas
Demonstrates full-stack API development skills
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# ============= SQLAlchemy Models (Database) =============

class UserDB(Base):
    """SQLAlchemy User model for database operations."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============= Pydantic Models (API Schemas) =============

class UserBase(BaseModel):
    """Base user schema with common attributes."""
    
    username: str = Field(..., min_length=3, max_length=50, 
                         description="Username for login")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=100, 
                                     description="User's full name")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate username is alphanumeric with underscores."""
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric')
        return v


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(..., min_length=8, max_length=100,
                         description="User password (min 8 characters)")
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response (excludes sensitive data)."""
    
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2


class UserInDB(UserResponse):
    """Schema for user in database (includes hashed password)."""
    
    hashed_password: str


# ============= Token Schemas =============

class Token(BaseModel):
    """JWT token response schema."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Data encoded in JWT token."""
    
    username: Optional[str] = None
    scopes: list[str] = []


class LoginRequest(BaseModel):
    """Schema for login request."""
    
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")
