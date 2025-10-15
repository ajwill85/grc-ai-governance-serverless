# ISO Control Mapping: 27001, 27701, and 42001
## AWS AI Governance Framework - Control Overlap Analysis

**Project**: AWS AI Governance Framework with Policy-as-Code  
**Author**: AJ Williams  
**Date**: October 2025  
**Purpose**: Identify and prioritize overlapping controls across ISO 27001, 27701, and 42001 for phased implementation

---

## Executive Summary

This document maps overlapping controls across three critical ISO standards for AI governance and privacy:
- **ISO/IEC 27001:2022** - Information Security Management
- **ISO/IEC 27701:2019** - Privacy Information Management (extension of 27001)
- **ISO/IEC 42001:2023** - AI Management System

The phased approach prioritizes controls with maximum overlap (all 3 standards) in Phase 1, progressing to standard-specific controls in later phases.

---

## Phase 1: Triple-Overlap Controls (All 3 Standards)
**Priority**: CRITICAL | **Timeline**: Days 1-30

These controls appear across all three standards and form the foundation of the AI governance framework.

### 1. Access Control & Identity Management

| Control Area | ISO 27001 | ISO 27701 | ISO 42001 | Implementation |
|--------------|-----------|-----------|-----------|----------------|
| **User Access Management** | A.5.15, A.5.16 | 6.2.1, 6.3.1 | 5.2, 6.1.3 | AWS IAM policies, SageMaker role validation |
| **Privileged Access** | A.5.18 | 6.2.2 | 6.1.3 | Least privilege enforcement for ML resources |
| **Access Reviews** | A.5.18 | 6.2.3 | 6.1.4 | Automated quarterly access audits |

**Technical Implementation**:
- OPA policies enforcing least privilege for SageMaker roles
- Lambda function for automated IAM role analysis
- CloudTrail monitoring for privileged access to AI systems

---

### 2. Data Governance & Classification

| Control Area | ISO 27001 | ISO 27701 | ISO 42001 | Implementation |
|--------------|-----------|-----------|-----------|----------------|
| **Data Classification** | A.5.12 | 6.4.1, 6.5.1 | 6.2.1 | S3 bucket tagging, Glue Data Catalog |
| **Data Minimization** | A.5.34 | 6.4.2 | 6.2.2 | Policy checks on training data scope |
| **Data Retention** | A.5.34 | 6.4.3, 6.5.3 | 6.2.3 | S3 lifecycle policies, automated deletion |
| **Data Quality** | A.8.24 | 6.4.4 | 6.2.4, 7.3 | Data validation in ML pipelines |

**Technical Implementation**:
- Automated data classification using AWS Macie
- OPA policies enforcing data minimization principles
- S3 lifecycle rules based on data classification
- Data quality checks in SageMaker Processing jobs

---

### 3. Risk Management

| Control Area | ISO 27001 | ISO 27701 | ISO 42001 | Implementation |
|--------------|-----------|-----------|-----------|----------------|
| **Risk Assessment** | Clause 6.1.2 | Clause 5.2 | 6.1.1, 6.1.2 | AI system risk scoring framework |
| **Risk Treatment** | Clause 6.1.3 | Clause 5.3 | 6.1.5 | Automated control recommendations |
| **Risk Monitoring** | Clause 9.1 | Clause 9.1 | 6.1.6, 9.1 | CloudWatch dashboards, EventBridge |

**Technical Implementation**:
- Python risk assessment engine for AI models
- Risk scoring based on data sensitivity + model complexity
- Automated alerts for high-risk deployments

---

### 4. Security Controls for AI/ML Systems

| Control Area | ISO 27001 | ISO 27701 | ISO 42001 | Implementation |
|--------------|-----------|-----------|-----------|----------------|
| **Encryption** | A.8.24 | 6.6.1 | 6.3.1 | KMS encryption for data/models |
| **Network Security** | A.8.20, A.8.21 | 6.6.2 | 6.3.2 | VPC isolation for SageMaker |
| **Logging & Monitoring** | A.8.15, A.8.16 | 6.6.3, 6.7.1 | 6.3.3, 9.2 | CloudTrail, CloudWatch Logs |
| **Vulnerability Management** | A.8.8 | 6.6.4 | 6.3.4 | Container scanning, dependency checks |

**Technical Implementation**:
- OPA policies requiring encryption at rest/transit
- Security group validation for SageMaker endpoints
- Automated vulnerability scanning for ML containers
- Centralized logging to CloudWatch Logs

---

### 5. Documentation & Transparency

| Control Area | ISO 27001 | ISO 27701 | ISO 42001 | Implementation |
|--------------|-----------|-----------|-----------|----------------|
| **System Documentation** | A.5.37 | 6.8.1 | 7.2, 7.4 | Model cards, data lineage tracking |
| **Change Management** | A.8.32 | 6.8.2 | 7.5 | GitOps for model versioning |
| **Audit Trails** | A.8.15 | 6.7.1, 6.7.2 | 9.2.1 | Immutable logs in CloudWatch |

**Technical Implementation**:
- Automated model card generation
- SageMaker Model Registry for versioning
- S3 versioning for training data
- CloudTrail for complete audit trail

---

### 6. Incident Management

| Control Area | ISO 27001 | ISO 27701 | ISO 42001 | Implementation |
|--------------|-----------|-----------|-----------|----------------|
| **Incident Response** | A.5.24, A.5.25 | 6.9.1 | 8.1, 8.2 | Automated incident detection |
| **Breach Notification** | A.5.26 | 6.9.2 | 8.3 | SNS notifications, runbooks |

**Technical Implementation**:
- EventBridge rules for anomaly detection
- Lambda functions for automated response
- SNS/PagerDuty integration for alerts

---

## Phase 2: Double-Overlap Controls (2 of 3 Standards)
**Priority**: HIGH | **Timeline**: Days 31-60

### 2A. ISO 27001 + 27701 (Privacy & Security)

| Control Area | ISO 27001 | ISO 27701 | Implementation |
|--------------|-----------|-----------|----------------|
| **Privacy by Design** | A.5.34 | 6.10.1-6.10.3 | Privacy-enhancing technologies (PETs) |
| **Data Subject Rights** | A.5.34 | 6.11.1-6.11.5 | Automated data deletion workflows |
| **Third-Party Management** | A.5.19-5.23 | 6.12.1-6.12.3 | Vendor risk assessments |

**Technical Implementation**:
- Differential privacy for analytics
- Data anonymization pipelines
- Third-party API security scanning

---

### 2B. ISO 27001 + 42001 (Security & AI)

| Control Area | ISO 27001 | ISO 42001 | Implementation |
|--------------|-----------|-----------|----------------|
| **Model Security** | A.8.24 | 6.4.1-6.4.3 | Model encryption, adversarial testing |
| **Training Environment Security** | A.8.1-8.3 | 6.5.1 | Isolated training environments |
| **Continuous Monitoring** | A.8.16 | 9.2.2 | Model drift detection |

**Technical Implementation**:
- SageMaker Model Monitor for drift
- Adversarial robustness testing
- Secure training job configurations

---

### 2C. ISO 27701 + 42001 (Privacy & AI)

| Control Area | ISO 27701 | ISO 42001 | Implementation |
|--------------|-----------|-----------|----------------|
| **Fairness & Bias** | 6.13.1 | 7.6, 7.7 | Bias detection in training data |
| **Explainability** | 6.13.2 | 7.8 | SageMaker Clarify integration |
| **Human Oversight** | 6.13.3 | 7.9, 7.10 | Human-in-the-loop workflows |

**Technical Implementation**:
- Automated bias metrics calculation
- SageMaker Clarify for explainability
- Step Functions for approval workflows

---

## Phase 3: Single-Standard Controls
**Priority**: MEDIUM | **Timeline**: Days 61-90

### 3A. ISO 27001 Only
- Business continuity planning (A.5.29-5.30)
- Physical security (A.7.1-7.14)
- Supplier security (A.5.19-5.23)

### 3B. ISO 27701 Only
- Privacy notices (6.14.1-6.14.3)
- Consent management (6.15.1-6.15.2)
- Cross-border transfers (6.16.1-6.16.3)

### 3C. ISO 42001 Only
- AI ethics framework (7.11-7.13)
- Stakeholder engagement (5.3)
- AI system lifecycle management (6.7.1-6.7.5)

---

## Control Implementation Priority Matrix

```
┌─────────────────────────────────────────────────────────────┐
│  OVERLAP LEVEL  │  # CONTROLS  │  PHASE  │  DAYS  │  EFFORT │
├─────────────────────────────────────────────────────────────┤
│  Triple (3/3)   │     25       │    1    │  1-30  │  60%    │
│  Double (2/3)   │     18       │    2    │ 31-60  │  30%    │
│  Single (1/3)   │     12       │    3    │ 61-90  │  10%    │
└─────────────────────────────────────────────────────────────┘
```

---

## Technical Architecture Summary

### Core Components
1. **Policy Engine**: Open Policy Agent (OPA) for policy-as-code
2. **Scanning Engine**: Python + boto3 for AWS resource analysis
3. **Automation Layer**: Lambda + EventBridge for continuous monitoring
4. **Reporting Layer**: CloudWatch Dashboards + S3 for evidence collection
5. **Integration Layer**: APIs for Jira, Slack, and audit tools

### AWS Services Used
- **AI/ML**: SageMaker, Bedrock, Comprehend
- **Security**: IAM, KMS, Security Hub, Macie, GuardDuty
- **Governance**: Config, CloudTrail, Organizations
- **Data**: S3, Glue, Lake Formation, Athena
- **Automation**: Lambda, EventBridge, Step Functions, Systems Manager

---

## Success Metrics

### Phase 1 (Days 1-30)
- ✅ 25 triple-overlap controls implemented
- ✅ 100% of SageMaker resources scanned
- ✅ Automated policy enforcement active
- ✅ Compliance dashboard operational

### Phase 2 (Days 31-60)
- ✅ 18 double-overlap controls implemented
- ✅ Privacy-enhancing technologies deployed
- ✅ Bias detection integrated
- ✅ Third-party risk assessments automated

### Phase 3 (Days 61-90)
- ✅ 12 single-standard controls implemented
- ✅ Full audit trail capability
- ✅ Incident response playbooks tested
- ✅ Complete documentation published

---

## References

- ISO/IEC 27001:2022 - Information security, cybersecurity and privacy protection
- ISO/IEC 27701:2019 - Privacy information management systems
- ISO/IEC 42001:2023 - Artificial intelligence management system
- AWS Well-Architected Framework - Security Pillar
- NIST AI Risk Management Framework (AI RMF)

---

**Document Version**: 1.0  
**Last Updated**: October 2025  
**Next Review**: Phase 1 Completion (Day 30)
