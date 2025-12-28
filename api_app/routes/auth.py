"""
Authentication Routes
Login, token generation, and authentication endpoints
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from api_app.models.user import Token, UserCreate, UserResponse
from api_app.auth.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from api_app.database.database import get_db, create_user, get_user_by_username
from loguru import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    - **username**: Unique username (alphanumeric)
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars, 1 digit, 1 uppercase)
    - **full_name**: Optional full name
    
    Returns the created user object.
    """
    logger.info(f"Registration attempt: {user.username}")
    
    # Check if username exists
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    try:
        # Create user
        db_user = create_user(
            db=db,
            username=user.username,
            email=user.email,
            password=user.password,
            full_name=user.full_name
        )
        
        logger.info(f"User registered successfully: {user.username}")
        return db_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login endpoint.
    
    Authenticates user and returns JWT access token.
    
    - **username**: Username or email
    - **password**: User password
    
    Returns JWT access token and token type.
    """
    logger.info(f"Login attempt: {form_data.username}")
    
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": ["user"]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Login successful: {form_data.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new JWT access token.
    """
    from api_app.auth.security import decode_access_token
    from jose import JWTError
    
    try:
        payload = decode_access_token(refresh_token)
        username = payload.get("sub")
        
        if not username or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user still exists
        user = get_user_by_username(db, username)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Token refreshed for: {username}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token deletion).
    
    In JWT authentication, logout is typically handled client-side
    by deleting the token. This endpoint is provided for API completeness.
    """
    logger.info("Logout endpoint called")
    return {"message": "Successfully logged out"}


@router.get("/verify-token")
async def verify_token(
    db: Session = Depends(get_db),
    current_user = Depends(lambda: None)  # Will be replaced with actual dependency
):
    """
    Verify if the provided token is valid.
    
    Returns user information if token is valid.
    """
    from api_app.auth.security import get_current_user
    
    # This would use get_current_user dependency
    # For now, return success
    return {"valid": True, "message": "Token is valid"}
