"""
API v1 Router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, dashboard, scans, findings, aws_accounts, users

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(findings.router, prefix="/findings", tags=["findings"])
api_router.include_router(aws_accounts.router, prefix="/aws-accounts", tags=["aws-accounts"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
