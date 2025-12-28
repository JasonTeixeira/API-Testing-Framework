"""
Database Configuration and CRUD Operations
SQLAlchemy setup and database utility functions
"""

from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from api_app.models.user import UserDB, Base
from api_app.auth.security import get_password_hash
from loguru import logger

# Database URL - SQLite for development
DATABASE_URL = "sqlite:///./api_test.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============= Database Initialization =============

def init_db():
    """Initialize database and create tables."""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def get_db():
    """
    Get database session.
    Dependency for FastAPI endpoints.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============= User CRUD Operations =============

def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    is_superuser: bool = False
) -> UserDB:
    """
    Create a new user in database.
    
    Args:
        db: Database session
        username: Username
        email: Email address
        password: Plain text password (will be hashed)
        full_name: User's full name
        is_superuser: Whether user is superuser
        
    Returns:
        Created user object
        
    Raises:
        ValueError: If username or email already exists
    """
    # Check if username exists
    if get_user_by_username(db, username):
        raise ValueError(f"Username '{username}' already exists")
    
    # Check if email exists
    if get_user_by_email(db, email):
        raise ValueError(f"Email '{email}' already exists")
    
    # Create user
    hashed_password = get_password_hash(password)
    db_user = UserDB(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        is_superuser=is_superuser,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User created: {username}")
    return db_user


def get_user_by_id(db: Session, user_id: int) -> Optional[UserDB]:
    """
    Get user by ID.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(UserDB).filter(UserDB.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[UserDB]:
    """
    Get user by username.
    
    Args:
        db: Database session
        username: Username
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(UserDB).filter(UserDB.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[UserDB]:
    """
    Get user by email.
    
    Args:
        db: Database session
        email: Email address
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(UserDB).filter(UserDB.email == email).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[UserDB]:
    """
    Get list of users with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        
    Returns:
        List of user objects
    """
    query = db.query(UserDB)
    
    if is_active is not None:
        query = query.filter(UserDB.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


def update_user(
    db: Session,
    user_id: int,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    password: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[UserDB]:
    """
    Update user information.
    
    Args:
        db: Database session
        user_id: User ID to update
        email: New email (optional)
        full_name: New full name (optional)
        password: New password (optional, will be hashed)
        is_active: New active status (optional)
        
    Returns:
        Updated user object if found, None otherwise
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        logger.warning(f"User not found for update: {user_id}")
        return None
    
    # Update fields if provided
    if email is not None:
        # Check if new email already exists
        existing_user = get_user_by_email(db, email)
        if existing_user and existing_user.id != user_id:
            raise ValueError(f"Email '{email}' already exists")
        db_user.email = email
    
    if full_name is not None:
        db_user.full_name = full_name
    
    if password is not None:
        db_user.hashed_password = get_password_hash(password)
    
    if is_active is not None:
        db_user.is_active = is_active
    
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User updated: {db_user.username}")
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete user from database.
    
    Args:
        db: Database session
        user_id: User ID to delete
        
    Returns:
        True if user was deleted, False if not found
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        logger.warning(f"User not found for deletion: {user_id}")
        return False
    
    db.delete(db_user)
    db.commit()
    
    logger.info(f"User deleted: {db_user.username}")
    return True


def deactivate_user(db: Session, user_id: int) -> Optional[UserDB]:
    """
    Deactivate user (soft delete).
    
    Args:
        db: Database session
        user_id: User ID to deactivate
        
    Returns:
        Deactivated user object if found, None otherwise
    """
    return update_user(db, user_id, is_active=False)


def activate_user(db: Session, user_id: int) -> Optional[UserDB]:
    """
    Activate user.
    
    Args:
        db: Database session
        user_id: User ID to activate
        
    Returns:
        Activated user object if found, None otherwise
    """
    return update_user(db, user_id, is_active=True)


# ============= Database Seed/Fixtures =============

def seed_test_users(db: Session):
    """
    Seed database with test users for development/testing.
    
    Args:
        db: Database session
    """
    test_users = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "Admin123!",
            "full_name": "Admin User",
            "is_superuser": True
        },
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test123!",
            "full_name": "Test User",
            "is_superuser": False
        },
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "John123!",
            "full_name": "John Doe",
            "is_superuser": False
        }
    ]
    
    for user_data in test_users:
        try:
            if not get_user_by_username(db, user_data["username"]):
                create_user(db, **user_data)
                logger.info(f"Test user created: {user_data['username']}")
        except Exception as e:
            logger.error(f"Error creating test user: {e}")


def clear_all_users(db: Session):
    """
    Clear all users from database (for testing).
    
    Args:
        db: Database session
    """
    db.query(UserDB).delete()
    db.commit()
    logger.warning("All users cleared from database")


# ============= Database Statistics =============

def get_user_count(db: Session, is_active: Optional[bool] = None) -> int:
    """
    Get total count of users.
    
    Args:
        db: Database session
        is_active: Filter by active status
        
    Returns:
        Total number of users
    """
    query = db.query(UserDB)
    
    if is_active is not None:
        query = query.filter(UserDB.is_active == is_active)
    
    return query.count()
