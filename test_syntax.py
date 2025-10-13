#!/usr/bin/env python3
"""
Syntax and structure validation script
Tests code without requiring AWS credentials or dependencies
"""

import ast
import sys
from pathlib import Path


def check_python_syntax(file_path: Path) -> tuple[bool, str]:
    """Check if Python file has valid syntax"""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        ast.parse(code)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Run syntax checks on all Python files"""
    print("="*60)
    print("AWS AI Governance Framework - Syntax Validation")
    print("="*60)
    
    project_root = Path(__file__).parent
    python_files = [
        'scan_all.py',
        'scanners/__init__.py',
        'scanners/sagemaker_scanner.py',
        'scanners/iam_scanner.py',
        'scanners/s3_scanner.py',
    ]
    
    all_passed = True
    
    for file_path in python_files:
        full_path = project_root / file_path
        if not full_path.exists():
            print(f"❌ {file_path}: File not found")
            all_passed = False
            continue
        
        passed, message = check_python_syntax(full_path)
        status = "✅" if passed else "❌"
        print(f"{status} {file_path}: {message}")
        
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("✅ All syntax checks passed!")
        return 0
    else:
        print("❌ Some checks failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
