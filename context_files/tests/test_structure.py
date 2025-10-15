#!/usr/bin/env python3
"""
Structure validation - tests code logic without AWS dependencies
"""

import sys
from pathlib import Path


def test_dataclass_structure():
    """Test that dataclasses are properly defined"""
    print("\n[TEST] Checking dataclass structures...")
    
    # Read scanner files and check for dataclass definitions
    scanners_dir = Path(__file__).parent / 'scanners'
    
    expected_dataclasses = {
        'sagemaker_scanner.py': 'SecurityFinding',
        'iam_scanner.py': 'IAMFinding',
        's3_scanner.py': 'S3Finding'
    }
    
    for file_name, class_name in expected_dataclasses.items():
        file_path = scanners_dir / file_name
        with open(file_path, 'r') as f:
            content = f.read()
        
        if f'@dataclass' in content and f'class {class_name}' in content:
            print(f"  ✅ {file_name}: {class_name} dataclass found")
        else:
            print(f"  ❌ {file_name}: {class_name} dataclass missing")
            return False
    
    return True


def test_scanner_methods():
    """Test that scanners have required methods"""
    print("\n[TEST] Checking scanner methods...")
    
    scanners_dir = Path(__file__).parent / 'scanners'
    
    required_methods = {
        'sagemaker_scanner.py': ['scan_all', 'export_findings', 'print_summary'],
        'iam_scanner.py': ['scan_all', 'export_findings', 'print_summary'],
        's3_scanner.py': ['scan_all', 'export_findings', 'print_summary']
    }
    
    for file_name, methods in required_methods.items():
        file_path = scanners_dir / file_name
        with open(file_path, 'r') as f:
            content = f.read()
        
        for method in methods:
            if f'def {method}(' in content:
                print(f"  ✅ {file_name}: {method}() found")
            else:
                print(f"  ❌ {file_name}: {method}() missing")
                return False
    
    return True


def test_imports():
    """Test that imports are correct"""
    print("\n[TEST] Checking imports...")
    
    # Check scan_all.py imports
    scan_all = Path(__file__).parent / 'scan_all.py'
    with open(scan_all, 'r') as f:
        content = f.read()
    
    required_imports = [
        'from scanners import SageMakerScanner, IAMScanner, S3Scanner',
        'import argparse',
        'import json',
        'from datetime import datetime'
    ]
    
    for imp in required_imports:
        if imp in content:
            print(f"  ✅ scan_all.py: {imp}")
        else:
            print(f"  ❌ scan_all.py: {imp} missing")
            return False
    
    return True


def test_cli_arguments():
    """Test that CLI arguments are defined"""
    print("\n[TEST] Checking CLI arguments...")
    
    scan_all = Path(__file__).parent / 'scan_all.py'
    with open(scan_all, 'r') as f:
        content = f.read()
    
    required_args = ['--region', '--output', '--html']
    
    for arg in required_args:
        if f"'{arg}'" in content or f'"{arg}"' in content:
            print(f"  ✅ scan_all.py: {arg} argument found")
        else:
            print(f"  ❌ scan_all.py: {arg} argument missing")
            return False
    
    return True


def test_opa_policies():
    """Test that OPA policies exist and have basic structure"""
    print("\n[TEST] Checking OPA policies...")
    
    policies_dir = Path(__file__).parent / 'policies'
    
    expected_policies = [
        'sagemaker_encryption.rego',
        'sagemaker_network.rego',
        'iam_least_privilege.rego',
        'data_classification.rego'
    ]
    
    for policy_file in expected_policies:
        policy_path = policies_dir / policy_file
        
        if not policy_path.exists():
            print(f"  ❌ {policy_file}: File not found")
            return False
        
        with open(policy_path, 'r') as f:
            content = f.read()
        
        # Check for basic Rego structure
        if 'package ' in content and 'deny[' in content:
            print(f"  ✅ {policy_file}: Valid Rego structure")
        else:
            print(f"  ❌ {policy_file}: Invalid Rego structure")
            return False
    
    return True


def test_documentation():
    """Test that documentation files exist"""
    print("\n[TEST] Checking documentation...")
    
    project_root = Path(__file__).parent
    
    required_docs = [
        'README.md',
        'USAGE_GUIDE.md',
        'requirements.txt',
        'ISO_CONTROL_MAPPING.md',
        '90_DAY_IMPLEMENTATION_PLAN.md',
        'PROJECT_README.md'
    ]
    
    for doc in required_docs:
        doc_path = project_root / doc
        if doc_path.exists():
            print(f"  ✅ {doc}: Found")
        else:
            print(f"  ❌ {doc}: Missing")
            return False
    
    return True


def main():
    """Run all tests"""
    print("="*60)
    print("AWS AI Governance Framework - Structure Validation")
    print("="*60)
    
    tests = [
        ("Dataclass Structure", test_dataclass_structure),
        ("Scanner Methods", test_scanner_methods),
        ("Imports", test_imports),
        ("CLI Arguments", test_cli_arguments),
        ("OPA Policies", test_opa_policies),
        ("Documentation", test_documentation),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"\n❌ {test_name}: Exception - {str(e)}")
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ All structure tests passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure AWS credentials: aws configure")
        print("3. Run scanners: python3 scan_all.py --region us-east-1")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
