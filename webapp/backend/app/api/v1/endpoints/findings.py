"""
Findings API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.db.session import get_db
from app.db import models
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/")
async def list_findings(
    skip: int = 0,
    limit: int = 50,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    resource_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    List findings for the current user's company
    """
    # Get scans for this company
    scan_ids = db.query(models.Scan.id).filter(
        models.Scan.company_id == current_user.company_id
    ).subquery()
    
    query = db.query(models.Finding).filter(
        models.Finding.scan_id.in_(scan_ids)
    )
    
    if severity:
        query = query.filter(models.Finding.severity == severity)
    if status:
        query = query.filter(models.Finding.status == status)
    if resource_type:
        query = query.filter(models.Finding.resource_type == resource_type)
    
    findings = query.order_by(desc(models.Finding.created_at)).offset(skip).limit(limit).all()
    
    return {
        "findings": [
            {
                "id": f.id,
                "resource_type": f.resource_type,
                "resource_name": f.resource_name,
                "severity": f.severity,
                "issue": f.issue,
                "control": f.control,
                "remediation": f.remediation,
                "status": f.status,
                "region": f.region,
                "created_at": f.created_at
            }
            for f in findings
        ],
        "total": query.count()
    }


@router.get("/{finding_id}")
async def get_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get detailed finding information
    """
    # Verify finding belongs to user's company
    finding = db.query(models.Finding).join(models.Scan).filter(
        models.Finding.id == finding_id,
        models.Scan.company_id == current_user.company_id
    ).first()
    
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    return {
        "id": finding.id,
        "scan_id": finding.scan_id,
        "resource_type": finding.resource_type,
        "resource_name": finding.resource_name,
        "resource_arn": finding.resource_arn,
        "severity": finding.severity,
        "issue": finding.issue,
        "control": finding.control,
        "remediation": finding.remediation,
        "region": finding.region,
        "status": finding.status,
        "assigned_to_id": finding.assigned_to_id,
        "notes": finding.notes,
        "created_at": finding.created_at,
        "updated_at": finding.updated_at
    }


@router.patch("/{finding_id}")
async def update_finding(
    finding_id: int,
    status: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update finding status, assignment, or notes
    """
    finding = db.query(models.Finding).join(models.Scan).filter(
        models.Finding.id == finding_id,
        models.Scan.company_id == current_user.company_id
    ).first()
    
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    if status:
        finding.status = status
    if assigned_to_id is not None:
        finding.assigned_to_id = assigned_to_id
    if notes is not None:
        finding.notes = notes
    
    db.commit()
    db.refresh(finding)
    
    return {
        "id": finding.id,
        "status": finding.status,
        "assigned_to_id": finding.assigned_to_id,
        "notes": finding.notes,
        "message": "Finding updated successfully"
    }
