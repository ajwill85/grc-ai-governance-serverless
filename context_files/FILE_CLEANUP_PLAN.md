# File Cleanup Plan - Serverless Project

**Date**: October 14, 2025  
**Purpose**: Organize project by separating core functionality from documentation/context

---

## 📁 File Categories

### CORE FUNCTIONALITY (Keep in Root)
These files are **essential** for the application to work:

#### Infrastructure & Deployment
- ✅ `serverless.yml` - Infrastructure as Code (REQUIRED)
- ✅ `package.json` - Node.js dependencies (REQUIRED)
- ✅ `requirements.txt` - Python dependencies (REQUIRED)
- ✅ `.gitignore` - Git configuration (REQUIRED)
- ✅ `README.md` - Main project readme (REQUIRED)

#### Lambda Functions
- ✅ `lambda/` - All Lambda function code (REQUIRED)
  - `lambda/api/handler.py`
  - `lambda/workers/scanner.py`
  - `lambda/workers/scheduled.py`
  - `lambda/requirements.txt`

#### Scanners & Policies
- ✅ `scanners/` - AWS resource scanners (REQUIRED)
  - `scanners/sagemaker_scanner.py`
  - `scanners/iam_scanner.py`
  - `scanners/s3_scanner.py`
- ✅ `policies/` - OPA policy rules (REQUIRED)
  - All `.rego` files

#### Web Application
- ✅ `webapp/` - Full web application (REQUIRED)
  - `webapp/backend/` - FastAPI backend
  - `webapp/frontend/` - React frontend
  - `webapp/database/` - Database schemas

#### CLI Scripts (Optional but Useful)
- ✅ `scan_all.py` - CLI scanner utility
- ✅ `scan_all_buckets.py` - S3 scanner utility

---

## 📚 DOCUMENTATION FILES (Move to context_files/)

These files are **documentation only** - helpful but not required for functionality:

### Deployment & Migration Guides (11 files)
1. ❌ `AWS_DEPLOYMENT_GUIDE.md` - Original ECS deployment (not needed for serverless)
2. ❌ `SERVERLESS_DEPLOYMENT.md` - Serverless deployment guide
3. ❌ `SERVERLESS_MIGRATION_GUIDE.md` - Migration guide
4. ❌ `QUICK_DEPLOY.md` - Quick deployment guide
5. ❌ `MIGRATION_APPLIED.md` - Migration change log
6. ❌ `MIGRATION_COMPLETE.md` - Migration summary
7. ❌ `migrate_to_serverless.sh` - Migration script (already applied)
8. ❌ `PRE_DEPLOYMENT_DEBUG_REPORT.md` - Pre-deployment checks
9. ❌ `PRE_PUSH_CHECKLIST.md` - Pre-push checklist
10. ❌ `USAGE_GUIDE.md` - Usage guide
11. ❌ `WEB_APP_DASHBOARD_GUIDE.md` - Dashboard guide

### Project Status & Planning (7 files)
12. ❌ `PROJECT_STATUS.md` - Project status
13. ❌ `PROJECT_COMPLETE.md` - Completion summary
14. ❌ `PROJECT_README.md` - Extended readme
15. ❌ `90_DAY_IMPLEMENTATION_PLAN.md` - Implementation plan
16. ❌ `ISO_CONTROL_MAPPING.md` - ISO control mapping
17. ❌ `VALIDATION_REPORT.md` - Validation report
18. ❌ `TESTING.md` - Testing guide

### Security & Analysis (5 files)
19. ❌ `SECURITY_AUDIT.md` - Security audit
20. ❌ `SECURITY_VERIFICATION.md` - Security verification
21. ❌ `COST_ANALYSIS.md` - Cost analysis
22. ❌ `CONVERSATION_CONTEXT.md` - Full conversation history
23. ❌ `GITHUB_SETUP.md` - GitHub setup guide

### Alternative README
24. ❌ `README_SERVERLESS.md` - Serverless-specific readme (duplicate of main README)

---

## 🗑️ GENERATED FILES (Move to context_files/)

These are **scan results** that should be in .gitignore:

25. ❌ `governance_scan_results.json` - Old scan results
26. ❌ `governance_scan_all_results.json` - Old scan results
27. ❌ `governance_scan_report.html` - Old scan report
28. ❌ `governance_scan_all_report.html` - Old scan report

---

## 🧪 TEST FILES (Move to context_files/)

These are **test scripts** used during development:

29. ❌ `test_structure.py` - Structure validation test
30. ❌ `test_syntax.py` - Syntax validation test

---

## 📦 LEGACY FILES (Move to context_files/)

These are from the **original ECS version** (not needed for serverless):

31. ❌ `task-definitions/` - ECS task definitions (not used in serverless)
  - `task-definitions/backend-task-definition.json`
  - `task-definitions/celery-worker-task-definition.json`

---

## 🗂️ MACOS METADATA (Delete)

These are **macOS resource fork files** (should be deleted):

- ❌ `._*` files (all 40+ of them) - macOS metadata, safe to delete

---

## 📋 Summary

### Keep in Root (Core Functionality)
- **5 config files**: serverless.yml, package.json, requirements.txt, .gitignore, README.md
- **3 directories**: lambda/, scanners/, policies/, webapp/
- **2 CLI scripts**: scan_all.py, scan_all_buckets.py
- **Total**: ~10 items

### Move to context_files/ (Documentation)
- **24 documentation files**: All .md files except README.md
- **4 scan result files**: governance_scan_*.json and *.html
- **2 test files**: test_*.py
- **1 directory**: task-definitions/
- **1 script**: migrate_to_serverless.sh
- **Total**: ~32 items

### Delete (macOS Metadata)
- **40+ ._* files**: macOS resource fork metadata
- **Total**: ~40 items

---

## 🎯 Recommended Structure After Cleanup

```
grc_ai_privacy_serverless/
├── README.md                    # Main readme (keep)
├── serverless.yml               # Infrastructure (keep)
├── package.json                 # Dependencies (keep)
├── requirements.txt             # Python deps (keep)
├── .gitignore                   # Git config (keep)
├── scan_all.py                  # CLI utility (keep)
├── scan_all_buckets.py          # CLI utility (keep)
├── lambda/                      # Lambda functions (keep)
├── scanners/                    # Scanners (keep)
├── policies/                    # OPA policies (keep)
├── webapp/                      # Web app (keep)
└── context_files/               # NEW: Documentation & context
    ├── deployment/
    │   ├── AWS_DEPLOYMENT_GUIDE.md
    │   ├── SERVERLESS_DEPLOYMENT.md
    │   ├── SERVERLESS_MIGRATION_GUIDE.md
    │   ├── QUICK_DEPLOY.md
    │   ├── MIGRATION_APPLIED.md
    │   ├── MIGRATION_COMPLETE.md
    │   ├── migrate_to_serverless.sh
    │   ├── PRE_DEPLOYMENT_DEBUG_REPORT.md
    │   └── PRE_PUSH_CHECKLIST.md
    ├── project_docs/
    │   ├── PROJECT_STATUS.md
    │   ├── PROJECT_COMPLETE.md
    │   ├── PROJECT_README.md
    │   ├── 90_DAY_IMPLEMENTATION_PLAN.md
    │   ├── ISO_CONTROL_MAPPING.md
    │   ├── VALIDATION_REPORT.md
    │   ├── TESTING.md
    │   ├── USAGE_GUIDE.md
    │   └── WEB_APP_DASHBOARD_GUIDE.md
    ├── security_analysis/
    │   ├── SECURITY_AUDIT.md
    │   ├── SECURITY_VERIFICATION.md
    │   ├── COST_ANALYSIS.md
    │   └── CONVERSATION_CONTEXT.md
    ├── scan_results/
    │   ├── governance_scan_results.json
    │   ├── governance_scan_all_results.json
    │   ├── governance_scan_report.html
    │   └── governance_scan_all_report.html
    ├── tests/
    │   ├── test_structure.py
    │   └── test_syntax.py
    ├── legacy/
    │   ├── task-definitions/
    │   └── README_SERVERLESS.md
    └── github/
        └── GITHUB_SETUP.md
```

---

## ✅ Benefits of This Organization

1. **Cleaner Root Directory**
   - Only 10 essential items in root
   - Easy to understand project structure
   - Clear separation of concerns

2. **Preserved Context**
   - All documentation preserved in context_files/
   - Organized by category
   - Easy to reference when needed

3. **Better Git Hygiene**
   - Scan results moved (should be gitignored)
   - macOS metadata removed
   - Cleaner git status

4. **Easier Deployment**
   - Only essential files in root
   - Faster zip/deploy operations
   - Reduced confusion

5. **Maintained History**
   - CONVERSATION_CONTEXT.md preserved
   - All migration docs preserved
   - Full project history available

---

## 🚀 Next Steps

Run the cleanup script to:
1. Create context_files/ directory structure
2. Move all documentation files
3. Delete macOS metadata files
4. Update README.md to reference context_files/
5. Update .gitignore if needed

**Estimated time**: 2 minutes  
**Risk**: Low (all files preserved, just moved)  
**Reversible**: Yes (can move files back)

---

**Ready to proceed with cleanup?**
