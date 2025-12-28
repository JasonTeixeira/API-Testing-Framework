"""
Security & Authentication Module
JWT token generation, password hashing, and authentication utilities
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from loguru import logger

# Configuration
SECRET_KEY = "your-secret-key-change-in-production-use-env-var"  # Use .env in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ============= Password Utilities =============

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(char in special_chars for char in password):
        return False, "Password must contain at least one special character"
    
    return True, ""


# ============= JWT Token Utilities =============

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Created access token for: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        raise


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token decode error: {e}")
        raise


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time delta
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)  # 7 days for refresh
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ============= Authentication Functions =============

def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticate a user with username and password.
    
    Args:
        db: Database session
        username: Username or email
        password: Plain text password
        
    Returns:
        User object if authentication successful, None otherwise
    """
    from api_app.database.database import get_user_by_username
    
    user = get_user_by_username(db, username)
    
    if not user:
        logger.warning(f"Authentication failed: User not found - {username}")
        return None
    
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: Invalid password for - {username}")
        return None
    
    if not user.is_active:
        logger.warning(f"Authentication failed: User inactive - {username}")
        return None
    
    logger.info(f"User authenticated successfully: {username}")
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = None  # Will be injected by FastAPI
):
    """
    Get current authenticated user from token.
    
    Args:
        token: JWT access token
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    from api_app.database.database import get_user_by_username
    
    user = get_user_by_username(db, username=username)
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Get current active user (convenience function).
    
    Args:
        current_user: Current user from token
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user = Depends(get_current_user)
):
    """
    Get current user if they are a superuser.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Superuser object
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# ============= API Key Authentication (Alternative) =============

class APIKeyAuth:
    """API Key authentication for service-to-service communication."""
    
    def __init__(self):
        self.api_keys = {
            "test_api_key_123": "test_service",
            "prod_api_key_456": "prod_service"
        }
    
    def validate_api_key(self, api_key: str) -> Optional[str]:
        """
        Validate API key and return service name.
        
        Args:
            api_key: API key string
            
        Returns:
            Service name if valid, None otherwise
        """
        return self.api_keys.get(api_key)
    
    def create_api_key(self, service_name: str) -> str:
        """
        Generate a new API key for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Generated API key
        """
        import secrets
        api_key = f"{service_name}_{secrets.token_urlsafe(32)}"
        self.api_keys[api_key] = service_name
        return api_key


# Global API key auth instance
api_key_auth = APIKeyAuth()
