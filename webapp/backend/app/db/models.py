"""
Database Models
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Company(Base):
    """Company/Organization model"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="company")
    aws_accounts = relationship("AWSAccount", back_populates="company")
    scans = relationship("Scan", back_populates="company")


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String(50), default="viewer")  # admin, editor, viewer, auditor
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    company = relationship("Company", back_populates="users")


class AWSAccount(Base):
    """AWS Account model"""
    __tablename__ = "aws_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    account_id = Column(String(12), nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    role_arn = Column(String(512), nullable=False)
    external_id = Column(String(255), nullable=False)
    regions = Column(JSON, default=["us-east-1"])  # List of regions to scan
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_scan_at = Column(DateTime(timezone=True))
    
    # Relationships
    company = relationship("Company", back_populates="aws_accounts")
    scans = relationship("Scan", back_populates="aws_account")


class Scan(Base):
    """Scan execution model"""
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    aws_account_id = Column(Integer, ForeignKey("aws_accounts.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    scan_type = Column(String(50), default="full")  # full, sagemaker, iam, s3
    region = Column(String(50))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    total_findings = Column(Integer, default=0)
    risk_score = Column(Integer, default=0)
    severity_breakdown = Column(JSON)  # {"CRITICAL": 3, "HIGH": 8, ...}
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="scans")
    aws_account = relationship("AWSAccount", back_populates="scans")
    findings = relationship("Finding", back_populates="scan")


class Finding(Base):
    """Security finding model"""
    __tablename__ = "findings"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_name = Column(String(255), nullable=False)
    resource_arn = Column(String(512))
    severity = Column(String(20), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    issue = Column(Text, nullable=False)
    control = Column(String(255), nullable=False)  # ISO control reference
    remediation = Column(Text, nullable=False)
    region = Column(String(50))
    status = Column(String(50), default="open")  # open, in_progress, resolved, accepted_risk
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    resolved_at = Column(DateTime(timezone=True))
    resolved_by_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    scan = relationship("Scan", back_populates="findings")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])


class ScanSchedule(Base):
    """Scheduled scan configuration"""
    __tablename__ = "scan_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    aws_account_id = Column(Integer, ForeignKey("aws_accounts.id"), nullable=False)
    schedule_type = Column(String(50), nullable=False)  # daily, weekly, monthly
    schedule_time = Column(String(10))  # HH:MM format
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True))
    next_run_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    aws_account = relationship("AWSAccount")


class DashboardPreference(Base):
    """User dashboard preferences"""
    __tablename__ = "dashboard_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    dashboard_view = Column(String(50), default="hybrid")  # hybrid, executive, technical
    theme = Column(String(20), default="light")  # light, dark
    widgets = Column(JSON)  # Widget configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
