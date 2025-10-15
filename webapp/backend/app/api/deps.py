"""
API Dependencies
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Get current authenticated user
    TODO: Implement JWT token validation
    
    For now, returns a mock user for development/testing
    """
    # PLACEHOLDER: In production, validate JWT token here
    # For now, return a mock user for testing
    
    # Check if any users exist
    user = db.query(models.User).first()
    
    if not user:
        # Create a demo user if none exists
        company = db.query(models.Company).first()
        if not company:
            company = models.Company(
                name="Demo Company",
                slug="demo-company"
            )
            db.add(company)
            db.commit()
            db.refresh(company)
        
        user = models.User(
            email="demo@example.com",
            hashed_password="placeholder",
            full_name="Demo User",
            company_id=company.id,
            role="admin",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Get current active user (not disabled)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_admin(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Require admin role
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
