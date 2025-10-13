"""
Scans API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.db import models
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/")
async def list_scans(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    List all scans for the current user's company
    """
    query = db.query(models.Scan).filter(
        models.Scan.company_id == current_user.company_id
    )
    
    if status:
        query = query.filter(models.Scan.status == status)
    
    scans = query.order_by(desc(models.Scan.created_at)).offset(skip).limit(limit).all()
    
    return {
        "scans": [
            {
                "id": scan.id,
                "status": scan.status,
                "scan_type": scan.scan_type,
                "region": scan.region,
                "total_findings": scan.total_findings,
                "risk_score": scan.risk_score,
                "started_at": scan.started_at,
                "completed_at": scan.completed_at,
                "duration_seconds": scan.duration_seconds
            }
            for scan in scans
        ],
        "total": query.count()
    }


@router.get("/{scan_id}")
async def get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get detailed scan information
    """
    scan = db.query(models.Scan).filter(
        models.Scan.id == scan_id,
        models.Scan.company_id == current_user.company_id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {
        "id": scan.id,
        "status": scan.status,
        "scan_type": scan.scan_type,
        "region": scan.region,
        "total_findings": scan.total_findings,
        "risk_score": scan.risk_score,
        "severity_breakdown": scan.severity_breakdown,
        "started_at": scan.started_at,
        "completed_at": scan.completed_at,
        "duration_seconds": scan.duration_seconds,
        "error_message": scan.error_message
    }


@router.post("/trigger")
async def trigger_scan(
    aws_account_id: int,
    scan_type: str = "full",
    region: str = "us-east-1",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Trigger a new scan
    TODO: Integrate with Celery task queue
    """
    # Verify AWS account belongs to user's company
    aws_account = db.query(models.AWSAccount).filter(
        models.AWSAccount.id == aws_account_id,
        models.AWSAccount.company_id == current_user.company_id
    ).first()
    
    if not aws_account:
        raise HTTPException(status_code=404, detail="AWS account not found")
    
    # Create scan record
    scan = models.Scan(
        company_id=current_user.company_id,
        aws_account_id=aws_account_id,
        status="pending",
        scan_type=scan_type,
        region=region,
        started_at=datetime.utcnow()
    )
    
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    # TODO: Queue Celery task here
    # celery_app.send_task('run_scan', args=[scan.id])
    
    return {
        "scan_id": scan.id,
        "status": "pending",
        "message": "Scan queued successfully (Celery integration pending)"
    }
