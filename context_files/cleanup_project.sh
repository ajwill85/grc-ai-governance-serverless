#!/bin/bash

# Project Cleanup Script
# Organizes files by moving documentation to context_files/

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Project Cleanup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Create context_files directory structure
print_info "Creating context_files directory structure..."
mkdir -p context_files/deployment
mkdir -p context_files/project_docs
mkdir -p context_files/security_analysis
mkdir -p context_files/scan_results
mkdir -p context_files/tests
mkdir -p context_files/legacy
mkdir -p context_files/github
print_status "Directory structure created"

# Move deployment documentation
print_info "Moving deployment documentation..."
mv AWS_DEPLOYMENT_GUIDE.md context_files/deployment/ 2>/dev/null || true
mv SERVERLESS_DEPLOYMENT.md context_files/deployment/ 2>/dev/null || true
mv SERVERLESS_MIGRATION_GUIDE.md context_files/deployment/ 2>/dev/null || true
mv QUICK_DEPLOY.md context_files/deployment/ 2>/dev/null || true
mv MIGRATION_APPLIED.md context_files/deployment/ 2>/dev/null || true
mv MIGRATION_COMPLETE.md context_files/deployment/ 2>/dev/null || true
mv migrate_to_serverless.sh context_files/deployment/ 2>/dev/null || true
mv PRE_DEPLOYMENT_DEBUG_REPORT.md context_files/deployment/ 2>/dev/null || true
mv PRE_PUSH_CHECKLIST.md context_files/deployment/ 2>/dev/null || true
print_status "Deployment docs moved"

# Move project documentation
print_info "Moving project documentation..."
mv PROJECT_STATUS.md context_files/project_docs/ 2>/dev/null || true
mv PROJECT_COMPLETE.md context_files/project_docs/ 2>/dev/null || true
mv PROJECT_README.md context_files/project_docs/ 2>/dev/null || true
mv 90_DAY_IMPLEMENTATION_PLAN.md context_files/project_docs/ 2>/dev/null || true
mv ISO_CONTROL_MAPPING.md context_files/project_docs/ 2>/dev/null || true
mv VALIDATION_REPORT.md context_files/project_docs/ 2>/dev/null || true
mv TESTING.md context_files/project_docs/ 2>/dev/null || true
mv USAGE_GUIDE.md context_files/project_docs/ 2>/dev/null || true
mv WEB_APP_DASHBOARD_GUIDE.md context_files/project_docs/ 2>/dev/null || true
print_status "Project docs moved"

# Move security and analysis documentation
print_info "Moving security and analysis documentation..."
mv SECURITY_AUDIT.md context_files/security_analysis/ 2>/dev/null || true
mv SECURITY_VERIFICATION.md context_files/security_analysis/ 2>/dev/null || true
mv COST_ANALYSIS.md context_files/security_analysis/ 2>/dev/null || true
mv CONVERSATION_CONTEXT.md context_files/security_analysis/ 2>/dev/null || true
print_status "Security docs moved"

# Move scan results
print_info "Moving scan results..."
mv governance_scan_results.json context_files/scan_results/ 2>/dev/null || true
mv governance_scan_all_results.json context_files/scan_results/ 2>/dev/null || true
mv governance_scan_report.html context_files/scan_results/ 2>/dev/null || true
mv governance_scan_all_report.html context_files/scan_results/ 2>/dev/null || true
print_status "Scan results moved"

# Move test files
print_info "Moving test files..."
mv test_structure.py context_files/tests/ 2>/dev/null || true
mv test_syntax.py context_files/tests/ 2>/dev/null || true
print_status "Test files moved"

# Move legacy files
print_info "Moving legacy files..."
mv task-definitions context_files/legacy/ 2>/dev/null || true
mv README_SERVERLESS.md context_files/legacy/ 2>/dev/null || true
print_status "Legacy files moved"

# Move GitHub setup
print_info "Moving GitHub documentation..."
mv GITHUB_SETUP.md context_files/github/ 2>/dev/null || true
print_status "GitHub docs moved"

# Delete macOS metadata files
print_info "Removing macOS metadata files..."
find . -name "._*" -type f -delete 2>/dev/null || true
print_status "macOS metadata removed"

# Create README in context_files
print_info "Creating context_files README..."
cat > context_files/README.md << 'EOF'
# Context Files

This directory contains documentation, analysis, and context files that are not required for the application to function, but provide valuable information about the project.

## Directory Structure

### deployment/
Deployment guides and migration documentation:
- AWS_DEPLOYMENT_GUIDE.md - Original ECS deployment guide
- SERVERLESS_DEPLOYMENT.md - Serverless deployment guide
- SERVERLESS_MIGRATION_GUIDE.md - Migration methodology
- MIGRATION_APPLIED.md - List of changes made
- MIGRATION_COMPLETE.md - Migration summary
- migrate_to_serverless.sh - Migration script (already applied)
- Other deployment-related docs

### project_docs/
Project status, planning, and documentation:
- PROJECT_STATUS.md - Current project status
- PROJECT_COMPLETE.md - Completion summary
- 90_DAY_IMPLEMENTATION_PLAN.md - Implementation roadmap
- ISO_CONTROL_MAPPING.md - ISO control mapping
- TESTING.md - Testing guide
- USAGE_GUIDE.md - Usage guide
- WEB_APP_DASHBOARD_GUIDE.md - Dashboard guide

### security_analysis/
Security audits and cost analysis:
- SECURITY_AUDIT.md - Security audit report
- SECURITY_VERIFICATION.md - Security verification
- COST_ANALYSIS.md - Detailed cost breakdown
- CONVERSATION_CONTEXT.md - Complete project history

### scan_results/
Old scan results (should be regenerated):
- governance_scan_*.json - JSON scan results
- governance_scan_*.html - HTML scan reports

### tests/
Test scripts used during development:
- test_structure.py - Structure validation
- test_syntax.py - Syntax validation

### legacy/
Files from original ECS version:
- task-definitions/ - ECS task definitions (not used in serverless)
- README_SERVERLESS.md - Duplicate readme

### github/
GitHub setup documentation:
- GITHUB_SETUP.md - GitHub repository setup guide

## Usage

These files are preserved for reference but are not required for the application to run. You can:

1. **Reference documentation** when needed
2. **Review project history** via CONVERSATION_CONTEXT.md
3. **Understand costs** via COST_ANALYSIS.md
4. **Deploy using guides** in deployment/
5. **Delete this entire directory** if you only need the working code

## Core Application Files

The core application files remain in the root directory:
- serverless.yml - Infrastructure as Code
- package.json - Node.js dependencies
- requirements.txt - Python dependencies
- lambda/ - Lambda function code
- scanners/ - AWS resource scanners
- policies/ - OPA policy rules
- webapp/ - Web application
- README.md - Main project readme
EOF
print_status "context_files README created"

# Update main README to reference context_files
print_info "Updating main README..."
cat >> README.md << 'EOF'

---

## 📚 Additional Documentation

Comprehensive documentation has been organized in the `context_files/` directory:

- **Deployment Guides**: `context_files/deployment/`
- **Project Documentation**: `context_files/project_docs/`
- **Security & Cost Analysis**: `context_files/security_analysis/`
- **Project History**: `context_files/security_analysis/CONVERSATION_CONTEXT.md`

See `context_files/README.md` for a complete index.
EOF
print_status "Main README updated"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Summary:"
echo "  ✓ Created context_files/ directory"
echo "  ✓ Moved 24 documentation files"
echo "  ✓ Moved 4 scan result files"
echo "  ✓ Moved 2 test files"
echo "  ✓ Moved legacy files"
echo "  ✓ Deleted macOS metadata files"
echo "  ✓ Updated README.md"
echo ""
echo "Root directory now contains only essential files:"
echo "  - serverless.yml"
echo "  - package.json"
echo "  - requirements.txt"
echo "  - README.md"
echo "  - .gitignore"
echo "  - lambda/"
echo "  - scanners/"
echo "  - policies/"
echo "  - webapp/"
echo "  - scan_all.py"
echo "  - scan_all_buckets.py"
echo ""
echo "All documentation preserved in: context_files/"
echo ""
