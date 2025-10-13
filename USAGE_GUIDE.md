# Usage Guide - AWS AI Governance Framework

Quick reference guide for using the scanners and policies.

## 🚀 Getting Started

### 1. Setup Environment

```bash
# Clone repository
cd grc_ai_privacy

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
```

### 2. Run Your First Scan

```bash
# Run unified scan (all scanners)
python scan_all.py --region us-east-1

# View results
cat governance_scan_results.json
open governance_scan_report.html  # macOS
```

## 📋 Individual Scanners

### SageMaker Scanner

Scans SageMaker notebooks, training jobs, models, and endpoints.

```bash
# Basic scan
python -m scanners.sagemaker_scanner

# Specify region and output
python -m scanners.sagemaker_scanner \
    --region us-west-2 \
    --output my_sagemaker_findings.json
```

**What it checks:**
- ✅ Encryption at rest (KMS)
- ✅ Root access disabled
- ✅ VPC configuration
- ✅ Network isolation
- ✅ Required tags (DataClassification, Owner, Purpose)
- ✅ Inter-container traffic encryption

### IAM Scanner

Analyzes IAM roles used by SageMaker for least privilege violations.

```bash
# Scan IAM roles
python -m scanners.iam_scanner

# Output saved to iam_findings.json
```

**What it checks:**
- ✅ Wildcard actions (*)
- ✅ Wildcard resources (*)
- ✅ Dangerous permissions (DeleteRole, DisableKey, etc.)
- ✅ Stale roles (not used in 90+ days)
- ✅ Cross-account access without conditions

### S3 Scanner

Checks S3 buckets used by SageMaker for data governance violations.

```bash
# Scan S3 buckets
python -m scanners.s3_scanner --region us-east-1

# Output saved to s3_findings.json
```

**What it checks:**
- ✅ Data classification tags
- ✅ Encryption enabled
- ✅ Versioning enabled
- ✅ Lifecycle policies configured
- ✅ Public access blocked

## 🔍 Understanding Results

### Severity Levels

- **CRITICAL**: Immediate action required (e.g., unencrypted PII data)
- **HIGH**: Important security issue (e.g., missing encryption)
- **MEDIUM**: Best practice violation (e.g., no versioning)
- **LOW**: Minor issue (e.g., missing tags)

### Sample Finding

```json
{
  "resource_type": "AWS::SageMaker::NotebookInstance",
  "resource_name": "ml-notebook-dev",
  "resource_arn": "arn:aws:sagemaker:us-east-1:123456789012:notebook-instance/ml-notebook-dev",
  "severity": "HIGH",
  "issue": "Notebook instance does not have KMS encryption enabled",
  "control": "ISO 27001 A.8.24, ISO 27701 6.6.1",
  "remediation": "Enable KMS encryption for the notebook instance",
  "timestamp": "2025-10-12T20:30:00Z",
  "region": "us-east-1"
}
```

## 🛠️ OPA Policy Testing

### Install OPA

```bash
# macOS
brew install opa

# Linux
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa
sudo mv opa /usr/local/bin/
```

### Test Policies

```bash
# Run all policy tests
opa test policies/ -v

# Test specific policy
opa test policies/sagemaker_encryption.rego -v
```

### Evaluate Policy Against Data

```bash
# Create test input
cat > test_notebook.json << EOF
{
  "resource_type": "AWS::SageMaker::NotebookInstance",
  "notebook_name": "test-notebook",
  "kms_key_id": null,
  "root_access": "Enabled"
}
EOF

# Evaluate policy
opa eval -d policies/sagemaker_encryption.rego \
         -i test_notebook.json \
         "data.sagemaker.encryption.deny"
```

## 📊 Report Formats

### JSON Report

```bash
python scan_all.py --output results.json
```

Contains:
- Scan metadata (timestamp, region)
- Findings by scanner
- Consolidated findings
- Summary statistics
- Risk score

### HTML Report

```bash
python scan_all.py --html report.html
open report.html
```

Includes:
- Executive summary
- Severity breakdown
- Top violated controls
- Detailed findings table
- Visual formatting

## 🎯 Common Use Cases

### 1. Pre-Deployment Security Check

```bash
# Before deploying new SageMaker resources
python -m scanners.sagemaker_scanner --region us-east-1

# Review findings
cat sagemaker_findings.json | jq '.findings[] | select(.severity=="CRITICAL" or .severity=="HIGH")'
```

### 2. Compliance Audit Preparation

```bash
# Run full scan
python scan_all.py --region us-east-1

# Generate HTML report for auditors
python scan_all.py --html audit_report.html

# Filter by specific control
cat governance_scan_results.json | jq '.consolidated_findings[] | select(.control | contains("ISO 27001 A.8.24"))'
```

### 3. Continuous Monitoring

```bash
# Add to cron job (daily at 2 AM)
0 2 * * * cd /path/to/grc_ai_privacy && python scan_all.py --output daily_scan_$(date +\%Y\%m\%d).json
```

### 4. Multi-Region Scan

```bash
# Scan multiple regions
for region in us-east-1 us-west-2 eu-west-1; do
    echo "Scanning $region..."
    python scan_all.py --region $region --output scan_${region}.json
done
```

## 🔧 Troubleshooting

### AWS Credentials Not Found

```bash
# Check AWS configuration
aws sts get-caller-identity

# If not configured
aws configure
```

### Permission Denied Errors

Ensure your IAM user/role has these permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:List*",
        "sagemaker:Describe*",
        "iam:List*",
        "iam:Get*",
        "s3:List*",
        "s3:GetBucket*"
      ],
      "Resource": "*"
    }
  ]
}
```

### No Resources Found

```bash
# Verify SageMaker resources exist
aws sagemaker list-notebook-instances --region us-east-1

# Check if buckets have SageMaker tag
aws s3api list-buckets
```

## 📈 Interpreting Risk Scores

Risk scores are calculated based on severity weights:
- CRITICAL: 10 points
- HIGH: 5 points
- MEDIUM: 2 points
- LOW: 1 point

**Risk Score Interpretation:**
- **0-20**: Low risk - Minor issues only
- **21-50**: Medium risk - Some important issues
- **51-80**: High risk - Multiple critical/high issues
- **81-100**: Critical risk - Immediate action required

## 🎓 Next Steps

1. **Review Findings**: Start with CRITICAL and HIGH severity
2. **Remediate Issues**: Follow remediation guidance in findings
3. **Implement Automation**: Set up continuous monitoring
4. **Expand Coverage**: Add more policies and scanners
5. **Integrate with CI/CD**: Add to deployment pipeline

## 📚 Additional Resources

- [ISO Control Mapping](ISO_CONTROL_MAPPING.md) - Control details
- [90-Day Implementation Plan](90_DAY_IMPLEMENTATION_PLAN.md) - Full roadmap
- [OPA Documentation](https://www.openpolicyagent.org/docs/latest/) - Policy language reference
- [AWS SageMaker Security](https://docs.aws.amazon.com/sagemaker/latest/dg/security.html) - AWS best practices

## 💡 Tips

1. **Start Small**: Run individual scanners first to understand output
2. **Filter Results**: Use `jq` to filter JSON for specific findings
3. **Track Progress**: Compare scans over time to measure improvement
4. **Automate**: Schedule regular scans with cron or AWS EventBridge
5. **Customize**: Modify policies to match your organization's requirements

---

**Questions?** Check the main [README.md](README.md) or project documentation.
