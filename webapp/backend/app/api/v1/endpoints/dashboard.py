"""
Dashboard API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.db.session import get_db
from app.db import models
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get dashboard overview metrics (Option 3: Hybrid Dashboard)
    """
    company_id = current_user.company_id
    
    # Get latest scan
    latest_scan = db.query(models.Scan).filter(
        models.Scan.company_id == company_id,
        models.Scan.status == "completed"
    ).order_by(desc(models.Scan.completed_at)).first()
    
    # Get total findings from latest scan
    total_findings = 0
    risk_score = 0
    severity_breakdown = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    
    if latest_scan:
        total_findings = latest_scan.total_findings
        risk_score = latest_scan.risk_score
        severity_breakdown = latest_scan.severity_breakdown or severity_breakdown
    
    # Calculate compliance rate (simplified)
    total_controls = 55  # ISO 27001 + 27701 + 42001
    violated_controls = len(set([
        f.control for f in db.query(models.Finding).filter(
            models.Finding.scan_id == latest_scan.id if latest_scan else None,
            models.Finding.status == "open"
        ).all()
    ])) if latest_scan else 0
    
    compliance_rate = ((total_controls - violated_controls) / total_controls * 100) if total_controls > 0 else 0
    
    # Get AWS accounts count
    aws_accounts_count = db.query(models.AWSAccount).filter(
        models.AWSAccount.company_id == company_id,
        models.AWSAccount.is_active == True
    ).count()
    
    # Get recent activity
    recent_scans = db.query(models.Scan).filter(
        models.Scan.company_id == company_id
    ).order_by(desc(models.Scan.created_at)).limit(5).all()
    
    recent_activity = []
    for scan in recent_scans:
        activity_type = "scan_completed" if scan.status == "completed" else "scan_failed"
        recent_activity.append({
            "type": activity_type,
            "description": f"Scan {scan.status} for account {scan.aws_account_id}",
            "timestamp": scan.completed_at or scan.created_at,
            "scan_id": scan.id
        })
    
    return {
        "risk_score": risk_score,
        "total_findings": total_findings,
        "compliance_rate": round(compliance_rate, 1),
        "last_scan": latest_scan.completed_at if latest_scan else None,
        "severity_breakdown": severity_breakdown,
        "aws_accounts_count": aws_accounts_count,
        "recent_activity": recent_activity
    }


@router.get("/trends")
async def get_compliance_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get compliance trends over time
    """
    company_id = current_user.company_id
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get scans in date range
    scans = db.query(models.Scan).filter(
        models.Scan.company_id == company_id,
        models.Scan.status == "completed",
        models.Scan.completed_at >= start_date
    ).order_by(models.Scan.completed_at).all()
    
    # Format trend data
    trend_data = []
    for scan in scans:
        trend_data.append({
            "date": scan.completed_at.isoformat(),
            "risk_score": scan.risk_score,
            "total_findings": scan.total_findings,
            "critical": scan.severity_breakdown.get("CRITICAL", 0) if scan.severity_breakdown else 0,
            "high": scan.severity_breakdown.get("HIGH", 0) if scan.severity_breakdown else 0,
            "medium": scan.severity_breakdown.get("MEDIUM", 0) if scan.severity_breakdown else 0,
            "low": scan.severity_breakdown.get("LOW", 0) if scan.severity_breakdown else 0,
        })
    
    return {
        "period_days": days,
        "data_points": len(trend_data),
        "trends": trend_data
    }


@router.get("/control-coverage")
async def get_control_coverage(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get ISO control coverage breakdown
    """
    company_id = current_user.company_id
    
    # Get latest scan
    latest_scan = db.query(models.Scan).filter(
        models.Scan.company_id == company_id,
        models.Scan.status == "completed"
    ).order_by(desc(models.Scan.completed_at)).first()
    
    if not latest_scan:
        return {
            "iso_27001": {"total": 25, "compliant": 0, "percentage": 0},
            "iso_27701": {"total": 18, "compliant": 0, "percentage": 0},
            "iso_42001": {"total": 12, "compliant": 0, "percentage": 0}
        }
    
    # Get violated controls
    violated_controls = db.query(models.Finding.control).filter(
        models.Finding.scan_id == latest_scan.id,
        models.Finding.status == "open"
    ).distinct().all()
    
    violated_set = set([c[0] for c in violated_controls])
    
    # Count by framework
    iso_27001_violated = len([c for c in violated_set if "ISO 27001" in c or "A." in c])
    iso_27701_violated = len([c for c in violated_set if "ISO 27701" in c or "6." in c])
    iso_42001_violated = len([c for c in violated_set if "ISO 42001" in c])
    
    return {
        "iso_27001": {
            "total": 25,
            "compliant": 25 - iso_27001_violated,
            "percentage": round((25 - iso_27001_violated) / 25 * 100, 1)
        },
        "iso_27701": {
            "total": 18,
            "compliant": 18 - iso_27701_violated,
            "percentage": round((18 - iso_27701_violated) / 18 * 100, 1)
        },
        "iso_42001": {
            "total": 12,
            "compliant": 12 - iso_42001_violated,
            "percentage": round((12 - iso_42001_violated) / 12 * 100, 1)
        }
    }


@router.get("/top-risks")
async def get_top_risks(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get top risks by frequency
    """
    company_id = current_user.company_id
    
    # Get latest scan
    latest_scan = db.query(models.Scan).filter(
        models.Scan.company_id == company_id,
        models.Scan.status == "completed"
    ).order_by(desc(models.Scan.completed_at)).first()
    
    if not latest_scan:
        return {"risks": []}
    
    # Group findings by issue and count
    risk_counts = db.query(
        models.Finding.issue,
        models.Finding.severity,
        func.count(models.Finding.id).label('count')
    ).filter(
        models.Finding.scan_id == latest_scan.id,
        models.Finding.status == "open"
    ).group_by(
        models.Finding.issue,
        models.Finding.severity
    ).order_by(
        desc('count')
    ).limit(limit).all()
    
    risks = []
    for issue, severity, count in risk_counts:
        risks.append({
            "issue": issue,
            "severity": severity,
            "count": count
        })
    
    return {"risks": risks}


@router.get("/remediation-progress")
async def get_remediation_progress(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get remediation progress statistics
    """
    company_id = current_user.company_id
    
    # Get all findings for company
    findings = db.query(models.Finding).join(models.Scan).filter(
        models.Scan.company_id == company_id
    ).all()
    
    status_counts = {
        "open": 0,
        "assigned": 0,
        "in_progress": 0,
        "resolved": 0,
        "accepted_risk": 0
    }
    
    for finding in findings:
        if finding.status == "open" and finding.assigned_to_id:
            status_counts["assigned"] += 1
        else:
            status_counts[finding.status] = status_counts.get(finding.status, 0) + 1
    
    return status_counts


@router.post("/preferences")
async def update_dashboard_preferences(
    preferences: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update user dashboard preferences
    """
    # Get or create preference
    pref = db.query(models.DashboardPreference).filter(
        models.DashboardPreference.user_id == current_user.id
    ).first()
    
    if not pref:
        pref = models.DashboardPreference(user_id=current_user.id)
        db.add(pref)
    
    # Update fields
    if "dashboard_view" in preferences:
        pref.dashboard_view = preferences["dashboard_view"]
    if "theme" in preferences:
        pref.theme = preferences["theme"]
    if "widgets" in preferences:
        pref.widgets = preferences["widgets"]
    
    db.commit()
    db.refresh(pref)
    
    return {
        "dashboard_view": pref.dashboard_view,
        "theme": pref.theme,
        "widgets": pref.widgets
    }


@router.get("/preferences")
async def get_dashboard_preferences(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get user dashboard preferences
    """
    pref = db.query(models.DashboardPreference).filter(
        models.DashboardPreference.user_id == current_user.id
    ).first()
    
    if not pref:
        # Return defaults
        return {
            "dashboard_view": "hybrid",
            "theme": "light",
            "widgets": None
        }
    
    return {
        "dashboard_view": pref.dashboard_view,
        "theme": pref.theme,
        "widgets": pref.widgets
    }
