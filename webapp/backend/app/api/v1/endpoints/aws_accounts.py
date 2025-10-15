"""
AWS Accounts API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.db import models
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/")
async def list_aws_accounts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    List all AWS accounts for the current user's company
    """
    accounts = db.query(models.AWSAccount).filter(
        models.AWSAccount.company_id == current_user.company_id
    ).all()
    
    return {
        "accounts": [
            {
                "id": acc.id,
                "account_id": acc.account_id,
                "account_name": acc.account_name,
                "regions": acc.regions,
                "is_active": acc.is_active,
                "last_scan_at": acc.last_scan_at,
                "created_at": acc.created_at
            }
            for acc in accounts
        ]
    }


@router.post("/")
async def create_aws_account(
    account_id: str,
    account_name: str,
    role_arn: str,
    external_id: str,
    regions: List[str] = ["us-east-1"],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Add a new AWS account
    """
    # Check if account already exists
    existing = db.query(models.AWSAccount).filter(
        models.AWSAccount.company_id == current_user.company_id,
        models.AWSAccount.account_id == account_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="AWS account already exists")
    
    # Create new account
    aws_account = models.AWSAccount(
        company_id=current_user.company_id,
        account_id=account_id,
        account_name=account_name,
        role_arn=role_arn,
        external_id=external_id,
        regions=regions,
        is_active=True
    )
    
    db.add(aws_account)
    db.commit()
    db.refresh(aws_account)
    
    return {
        "id": aws_account.id,
        "account_id": aws_account.account_id,
        "account_name": aws_account.account_name,
        "message": "AWS account added successfully"
    }


@router.get("/{account_id}")
async def get_aws_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get AWS account details
    """
    account = db.query(models.AWSAccount).filter(
        models.AWSAccount.id == account_id,
        models.AWSAccount.company_id == current_user.company_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="AWS account not found")
    
    return {
        "id": account.id,
        "account_id": account.account_id,
        "account_name": account.account_name,
        "role_arn": account.role_arn,
        "external_id": account.external_id,
        "regions": account.regions,
        "is_active": account.is_active,
        "last_scan_at": account.last_scan_at,
        "created_at": account.created_at
    }


@router.delete("/{account_id}")
async def delete_aws_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete (deactivate) an AWS account
    """
    account = db.query(models.AWSAccount).filter(
        models.AWSAccount.id == account_id,
        models.AWSAccount.company_id == current_user.company_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="AWS account not found")
    
    # Soft delete - just deactivate
    account.is_active = False
    db.commit()
    
    return {"message": "AWS account deactivated successfully"}


@router.post("/{account_id}/test-connection")
async def test_aws_connection(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Test AWS IAM role connection
    TODO: Implement actual STS assume role test
    """
    account = db.query(models.AWSAccount).filter(
        models.AWSAccount.id == account_id,
        models.AWSAccount.company_id == current_user.company_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="AWS account not found")
    
    # TODO: Implement actual boto3 STS assume role test
    # import boto3
    # sts = boto3.client('sts')
    # try:
    #     sts.assume_role(
    #         RoleArn=account.role_arn,
    #         RoleSessionName='GRCConnectionTest',
    #         ExternalId=account.external_id
    #     )
    #     return {"status": "success", "message": "Connection successful"}
    # except Exception as e:
    #     return {"status": "error", "message": str(e)}
    
    return {
        "status": "pending",
        "message": "Connection test not yet implemented - placeholder response"
    }
