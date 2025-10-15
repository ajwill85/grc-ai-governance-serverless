#!/bin/bash

# Folder Organization Script for GRC AI Governance Serverless
# Creates a clean, professional folder structure

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Folder Organization Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Create organized folder structure
print_info "Creating organized folder structure..."

# 1. Scripts folder for development/deployment scripts
mkdir -p scripts/local
mkdir -p scripts/deployment
print_status "Created scripts/ directory"

# 2. Config folder for configuration files
mkdir -p config
print_status "Created config/ directory"

# 3. Tests folder for test files
mkdir -p tests
print_status "Created tests/ directory"

# 4. Docs folder for quick reference docs
mkdir -p docs
print_status "Created docs/ directory"

# Move development scripts
print_info "Organizing development scripts..."
mv run_local_app.py scripts/local/ 2>/dev/null || true
mv start_local.sh scripts/local/ 2>/dev/null || true
mv test_local.py scripts/local/ 2>/dev/null || true
print_status "Development scripts moved to scripts/local/"

# Move CLI scanner scripts
print_info "Organizing CLI scanner scripts..."
mv scan_all.py scripts/ 2>/dev/null || true
mv scan_all_buckets.py scripts/ 2>/dev/null || true
print_status "Scanner scripts moved to scripts/"

# Move configuration files
print_info "Organizing configuration files..."
mv serverless-local.yml config/ 2>/dev/null || true
print_status "Configuration files moved to config/"

# Move documentation
print_info "Organizing documentation..."
mv LOCAL_RUNNING.md docs/ 2>/dev/null || true
print_status "Documentation moved to docs/"

# Move test database
print_info "Cleaning up test files..."
mv test.db tests/ 2>/dev/null || true
print_status "Test files moved to tests/"

# Delete macOS metadata
print_info "Removing macOS metadata..."
find . -name "._*" -type f -delete 2>/dev/null || true
print_status "macOS metadata removed"

# Create README files for each directory
print_info "Creating directory README files..."

cat > scripts/README.md << 'EOF'
# Scripts

This directory contains utility scripts for development and deployment.

## Local Development (`local/`)
- `run_local_app.py` - Run FastAPI backend locally
- `start_local.sh` - Start serverless offline with environment variables
- `test_local.py` - Test local API endpoints

## Scanner Scripts
- `scan_all.py` - Run all AWS governance scanners
- `scan_all_buckets.py` - Scan all S3 buckets for compliance

## Usage

### Run Local Development Server
```bash
cd scripts/local
python3 run_local_app.py
```

### Run Scanners
```bash
python3 scripts/scan_all.py --region us-east-1
python3 scripts/scan_all_buckets.py --region us-east-1
```
EOF

cat > config/README.md << 'EOF'
# Configuration Files

This directory contains configuration files for different environments.

## Files
- `serverless-local.yml` - Local development configuration for serverless offline

## Usage

Configuration files are automatically loaded by the respective tools.
EOF

cat > tests/README.md << 'EOF'
# Tests

This directory contains test files and test databases.

## Files
- `test.db` - SQLite database for local testing

## Running Tests

Tests are run automatically during development with hot reload enabled.
EOF

cat > docs/README.md << 'EOF'
# Documentation

Quick reference documentation for local development.

## Files
- `LOCAL_RUNNING.md` - Information about running servers locally

## More Documentation

For comprehensive documentation, see the `context_files/` directory:
- Deployment guides: `context_files/deployment/`
- Project docs: `context_files/project_docs/`
- Security analysis: `context_files/security_analysis/`
EOF

print_status "README files created"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Folder Organization Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "New folder structure:"
echo "  📁 scripts/"
echo "     ├── local/          (development scripts)"
echo "     ├── scan_all.py     (CLI scanner)"
echo "     └── scan_all_buckets.py"
echo ""
echo "  📁 config/             (configuration files)"
echo "  📁 tests/              (test files & databases)"
echo "  📁 docs/               (quick reference docs)"
echo ""
echo "  📁 lambda/             (Lambda functions)"
echo "  📁 scanners/           (Scanner modules)"
echo "  📁 policies/           (OPA policies)"
echo "  📁 webapp/             (Web application)"
echo "  📁 context_files/      (Documentation archive)"
echo ""
echo "Root directory now contains only:"
echo "  - serverless.yml"
echo "  - package.json"
echo "  - requirements.txt"
echo "  - README.md"
echo "  - .gitignore"
echo ""
