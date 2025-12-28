"""
User Management Routes
CRUD operations for user management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from api_app.models.user import UserResponse, UserUpdate
from api_app.database.database import (
    get_db,
    get_user_by_id,
    get_users,
    update_user,
    delete_user,
    deactivate_user,
    activate_user,
    get_user_count
)
from api_app.auth.security import get_current_active_user, get_current_superuser
from loguru import logger

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get list of users with pagination.
    
    Requires authentication.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100, max: 1000)
    - **is_active**: Filter by active status (optional)
    
    Returns list of users.
    """
    logger.info(f"Listing users: skip={skip}, limit={limit}, is_active={is_active}")
    
    users = get_users(db, skip=skip, limit=limit, is_active=is_active)
    
    logger.info(f"Retrieved {len(users)} users")
    return users


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    
    Returns the current user's profile.
    """
    logger.info(f"Current user info requested: {current_user.username}")
    return current_user


@router.get("/count")
async def count_users(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get total count of users.
    
    - **is_active**: Filter by active status (optional)
    
    Returns user count.
    """
    count = get_user_count(db, is_active=is_active)
    logger.info(f"User count: {count} (is_active={is_active})")
    
    return {
        "count": count,
        "is_active": is_active
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get user by ID.
    
    Requires authentication.
    
    - **user_id**: User ID to retrieve
    
    Returns user object.
    """
    logger.info(f"Get user: {user_id}")
    
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Non-superusers can only view their own profile or active users
    if not current_user.is_superuser:
        if db_user.id != current_user.id and not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this user"
            )
    
    return db_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Update current user's information.
    
    Users can update their own profile.
    
    - **email**: New email (optional)
    - **full_name**: New full name (optional)
    - **password**: New password (optional)
    
    Returns updated user object.
    """
    logger.info(f"Updating user: {current_user.username}")
    
    try:
        updated_user = update_user(
            db,
            user_id=current_user.id,
            email=user_update.email,
            full_name=user_update.full_name,
            password=user_update.password
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User updated: {current_user.username}")
        return updated_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_superuser)
):
    """
    Update user by ID (superuser only).
    
    Requires superuser privileges.
    
    - **user_id**: User ID to update
    - **email**: New email (optional)
    - **full_name**: New full name (optional)
    - **password**: New password (optional)
    - **is_active**: Active status (optional)
    
    Returns updated user object.
    """
    logger.info(f"Admin updating user: {user_id}")
    
    try:
        updated_user = update_user(
            db,
            user_id=user_id,
            email=user_update.email,
            full_name=user_update.full_name,
            password=user_update.password,
            is_active=user_update.is_active
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        logger.info(f"User {user_id} updated by admin")
        return updated_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_superuser)
):
    """
    Delete user by ID (superuser only).
    
    Requires superuser privileges.
    Permanently deletes the user from database.
    
    - **user_id**: User ID to delete
    
    Returns 204 No Content on success.
    """
    logger.info(f"Admin deleting user: {user_id}")
    
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = delete_user(db, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    logger.info(f"User {user_id} deleted by admin")
    return None


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_superuser)
):
    """
    Deactivate user (soft delete, superuser only).
    
    Requires superuser privileges.
    
    - **user_id**: User ID to deactivate
    
    Returns deactivated user object.
    """
    logger.info(f"Admin deactivating user: {user_id}")
    
    # Prevent self-deactivation
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    deactivated_user = deactivate_user(db, user_id)
    
    if not deactivated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    logger.info(f"User {user_id} deactivated by admin")
    return deactivated_user


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_superuser)
):
    """
    Activate user (superuser only).
    
    Requires superuser privileges.
    
    - **user_id**: User ID to activate
    
    Returns activated user object.
    """
    logger.info(f"Admin activating user: {user_id}")
    
    activated_user = activate_user(db, user_id)
    
    if not activated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    logger.info(f"User {user_id} activated by admin")
    return activated_user
