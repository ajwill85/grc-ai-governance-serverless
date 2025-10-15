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
