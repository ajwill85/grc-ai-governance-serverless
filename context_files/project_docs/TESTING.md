# Testing Guide - AWS AI Governance Framework

Comprehensive testing documentation for the AWS AI Governance Framework.

## 🎯 Testing Philosophy

This project uses a layered testing approach:
1. **Syntax validation** - Ensures Python code is syntactically correct
2. **Structure validation** - Verifies code architecture and components
3. **Unit tests** - Tests individual functions (requires dependencies)
4. **Integration tests** - Tests scanner workflows (requires AWS)
5. **Policy tests** - Validates OPA policies (requires OPA binary)

## 🚀 Quick Start (No Dependencies)

### 1. Syntax Validation

Validates that all Python files have correct syntax without requiring any dependencies.

```bash
python3 test_syntax.py
```

**What it checks:**
- ✅ Python syntax errors
- ✅ Import statements
- ✅ Function definitions
- ✅ Class structures

**Expected output:**
```
============================================================
AWS AI Governance Framework - Syntax Validation
============================================================
✅ scan_all.py: OK
✅ scanners/__init__.py: OK
✅ scanners/sagemaker_scanner.py: OK
✅ scanners/iam_scanner.py: OK
✅ scanners/s3_scanner.py: OK
============================================================
✅ All syntax checks passed!
```

### 2. Structure Validation

Validates code architecture and component structure without AWS dependencies.

```bash
python3 test_structure.py
```

**What it checks:**
- ✅ Dataclass definitions (SecurityFinding, IAMFinding, S3Finding)
- ✅ Scanner methods (scan_all, export_findings, print_summary)
- ✅ Import statements
- ✅ CLI arguments (--region, --output, --html)
- ✅ OPA policy files and structure
- ✅ Documentation files

**Expected output:**
```
============================================================
AWS AI Governance Framework - Structure Validation
============================================================

[TEST] Checking dataclass structures...
  ✅ sagemaker_scanner.py: SecurityFinding dataclass found
  ✅ iam_scanner.py: IAMFinding dataclass found
  ✅ s3_scanner.py: S3Finding dataclass found

[TEST] Checking scanner methods...
  ✅ sagemaker_scanner.py: scan_all() found
  ✅ sagemaker_scanner.py: export_findings() found
  ✅ sagemaker_scanner.py: print_summary() found
  ...

============================================================
✅ All structure tests passed!
```

## 🔧 Full Testing (Requires Dependencies)

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install OPA (macOS)
brew install opa

# Install OPA (Linux)
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa
sudo mv opa /usr/local/bin/
```

### 2. OPA Policy Testing

Test OPA policies for syntax and logic errors.

```bash
# Test all policies
opa test policies/ -v

# Test specific policy
opa test policies/sagemaker_encryption.rego -v

# Check policy syntax
opa check policies/
```

**Create test data:**

```bash
# Create test input for notebook without encryption
cat > test_data/unencrypted_notebook.json << EOF
{
  "resource_type": "AWS::SageMaker::NotebookInstance",
  "notebook_name": "test-notebook",
  "kms_key_id": null,
  "root_access": "Enabled",
  "direct_internet_access": "Enabled",
  "subnet_id": null
}
EOF

# Evaluate policy
opa eval -d policies/sagemaker_encryption.rego \
         -i test_data/unencrypted_notebook.json \
         "data.sagemaker.encryption.deny"
```

**Expected violations:**
```json
[
  "VIOLATION: SageMaker notebook 'test-notebook' must have KMS encryption enabled. Control: ISO 27001 A.8.24, ISO 27701 6.6.1",
  "VIOLATION: SageMaker notebook 'test-notebook' must disable root access. Control: ISO 27001 A.5.18"
]
```

### 3. Python Unit Tests (Future)

When unit tests are implemented:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=scanners --cov-report=html

# Run specific test file
pytest tests/test_sagemaker_scanner.py -v
```

### 4. Security Scanning

Check code for security vulnerabilities.

```bash
# Scan for security issues
bandit -r scanners/ scan_all.py

# Check dependency vulnerabilities
safety check

# Type checking
mypy scanners/ scan_all.py
```

## 🧪 Integration Testing (Requires AWS)

### Prerequisites

1. AWS credentials configured:
```bash
aws configure
```

2. Test AWS account with SageMaker resources (optional)

### Running Integration Tests

```bash
# Test SageMaker scanner
python3 -m scanners.sagemaker_scanner --region us-east-1

# Test IAM scanner
python3 -m scanners.iam_scanner

# Test S3 scanner
python3 -m scanners.s3_scanner --region us-east-1

# Test unified scanner
python3 scan_all.py --region us-east-1
```

### Creating Test Resources (Optional)

If you want to test with actual AWS resources:

```bash
# Create test SageMaker notebook (unencrypted - should trigger violations)
aws sagemaker create-notebook-instance \
    --notebook-instance-name test-governance-notebook \
    --instance-type ml.t3.medium \
    --role-arn arn:aws:iam::ACCOUNT_ID:role/SageMakerRole \
    --region us-east-1

# Run scanner to detect violations
python3 -m scanners.sagemaker_scanner --region us-east-1

# Clean up
aws sagemaker delete-notebook-instance \
    --notebook-instance-name test-governance-notebook \
    --region us-east-1
```

## 📊 Test Coverage Goals

### Current Status
- ✅ Syntax validation: 100%
- ✅ Structure validation: 100%
- 🔄 Unit tests: 0% (to be implemented)
- 🔄 Integration tests: Manual only
- ✅ OPA policies: Syntax validated

### Target Coverage
- **Unit tests**: 80%+ code coverage
- **Integration tests**: All scanners tested against real AWS resources
- **OPA policies**: 100% policy rules tested with sample data

## 🐛 Debugging

### Common Issues

**Issue: boto3 not found**
```bash
# Solution: Install dependencies
pip install boto3
```

**Issue: AWS credentials not configured**
```bash
# Solution: Configure AWS CLI
aws configure
```

**Issue: Permission denied errors**
```bash
# Solution: Ensure IAM permissions include:
# - sagemaker:List*, sagemaker:Describe*
# - iam:List*, iam:Get*
# - s3:List*, s3:GetBucket*
```

**Issue: OPA not found**
```bash
# Solution: Install OPA
brew install opa  # macOS
# or download from https://www.openpolicyagent.org/
```

### Debug Mode

Add verbose logging to scanners:

```python
# In scanner files, add at the top
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Writing Tests

### Example Unit Test (Future)

```python
# tests/test_sagemaker_scanner.py
import pytest
from scanners.sagemaker_scanner import SageMakerScanner, SecurityFinding

def test_finding_creation():
    """Test SecurityFinding dataclass"""
    finding = SecurityFinding(
        resource_type='AWS::SageMaker::NotebookInstance',
        resource_name='test-notebook',
        resource_arn='arn:aws:sagemaker:us-east-1:123456789012:notebook-instance/test',
        severity='HIGH',
        issue='Missing encryption',
        control='ISO 27001 A.8.24',
        remediation='Enable KMS encryption',
        timestamp='2025-10-12T20:00:00Z',
        region='us-east-1'
    )
    
    assert finding.severity == 'HIGH'
    assert 'ISO 27001' in finding.control
```

### Example OPA Test

```rego
# policies/sagemaker_encryption_test.rego
package sagemaker.encryption

test_deny_unencrypted_notebook {
    input := {
        "resource_type": "AWS::SageMaker::NotebookInstance",
        "notebook_name": "test-notebook",
        "kms_key_id": null
    }
    
    count(deny) > 0
}

test_allow_encrypted_notebook {
    input := {
        "resource_type": "AWS::SageMaker::NotebookInstance",
        "notebook_name": "test-notebook",
        "kms_key_id": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
    }
    
    count(deny) == 0
}
```

## 🎯 CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run syntax validation
      run: python3 test_syntax.py
    
    - name: Run structure validation
      run: python3 test_structure.py
    
    - name: Install OPA
      run: |
        curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
        chmod +x opa
        sudo mv opa /usr/local/bin/
    
    - name: Test OPA policies
      run: opa test policies/ -v
    
    - name: Security scan
      run: |
        pip install bandit safety
        bandit -r scanners/ scan_all.py
        safety check
```

## 📈 Test Metrics

Track these metrics for test quality:

- **Code coverage**: Target 80%+
- **Policy coverage**: 100% of deny rules tested
- **Test execution time**: < 5 minutes for full suite
- **Test reliability**: 0 flaky tests

## 🔍 Manual Testing Checklist

Before deploying or demonstrating:

- [ ] Run `python3 test_syntax.py` - All pass
- [ ] Run `python3 test_structure.py` - All pass
- [ ] Test each scanner individually
- [ ] Test unified scanner with `--region`, `--output`, `--html` flags
- [ ] Verify JSON output is valid
- [ ] Verify HTML report renders correctly
- [ ] Test OPA policies with sample data
- [ ] Check documentation is up to date

## 📚 Resources

- [pytest Documentation](https://docs.pytest.org/)
- [OPA Testing](https://www.openpolicyagent.org/docs/latest/policy-testing/)
- [boto3 Testing with moto](https://github.com/spulec/moto)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

**Last Updated**: October 2025  
**Status**: Syntax and structure validation complete, unit tests pending
