# 📁 Project Structure - GRC AI Governance Serverless

**Last Updated**: October 14, 2025  
**Status**: ✅ Organized & Clean

---

## 🏗️ Directory Structure

```
grc_ai_privacy_serverless/
│
├── 📄 Core Files (Root)
│   ├── README.md              # Main project documentation
│   ├── serverless.yml         # Infrastructure as Code
│   ├── package.json           # Node.js dependencies
│   ├── package-lock.json      # Locked dependencies
│   ├── requirements.txt       # Python dependencies
│   └── .gitignore            # Git ignore rules
│
├── 📁 lambda/                 # Lambda Functions
│   ├── api/
│   │   └── handler.py        # API Gateway handler
│   ├── workers/
│   │   ├── scanner.py        # SQS scan worker
│   │   └── scheduled.py      # EventBridge scheduler
│   ├── layers/
│   │   └── python/           # Lambda layers
│   └── requirements.txt      # Lambda-specific deps
│
├── 📁 scanners/              # AWS Resource Scanners
│   ├── __init__.py
│   ├── base_scanner.py       # Base scanner class
│   ├── sagemaker_scanner.py  # SageMaker scanner
│   ├── iam_scanner.py        # IAM scanner
│   └── s3_scanner.py         # S3 scanner
│
├── 📁 policies/              # OPA Policy Rules
│   ├── iso_27001/            # ISO 27001 controls
│   ├── iso_27701/            # ISO 27701 controls
│   ├── iso_42001/            # ISO 42001 controls
│   └── *.rego                # Policy rule files
│
├── 📁 webapp/                # Web Application
│   ├── backend/              # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py      # FastAPI app
│   │   │   ├── api/         # API endpoints
│   │   │   ├── core/        # Core utilities
│   │   │   ├── db/          # Database models
│   │   │   └── schemas/     # Pydantic schemas
│   │   └── requirements.txt  # Backend deps
│   │
│   ├── frontend/             # React frontend
│   │   ├── src/
│   │   │   ├── App.tsx      # Main app component
│   │   │   ├── pages/       # Page components
│   │   │   ├── components/  # Reusable components
│   │   │   ├── stores/      # State management
│   │   │   └── lib/         # Utilities
│   │   ├── package.json     # Frontend deps
│   │   └── vite.config.ts   # Vite configuration
│   │
│   └── database/             # Database schemas
│       └── init.sql         # Initial schema
│
├── 📁 scripts/               # Utility Scripts
│   ├── local/               # Local development
│   │   ├── run_local_app.py    # Run FastAPI locally
│   │   ├── start_local.sh      # Start serverless offline
│   │   └── test_local.py       # Test local endpoints
│   ├── scan_all.py          # Run all scanners
│   ├── scan_all_buckets.py  # S3 scanner CLI
│   ├── organize_folders.sh  # Folder organization
│   └── README.md            # Scripts documentation
│
├── 📁 config/                # Configuration Files
│   ├── serverless-local.yml # Local serverless config
│   └── README.md            # Config documentation
│
├── 📁 tests/                 # Test Files
│   ├── test.db              # SQLite test database
│   └── README.md            # Test documentation
│
├── 📁 docs/                  # Quick Reference Docs
│   ├── LOCAL_RUNNING.md     # Local server info
│   └── README.md            # Docs index
│
├── 📁 context_files/         # Documentation Archive
│   ├── deployment/          # Deployment guides
│   ├── project_docs/        # Project documentation
│   ├── security_analysis/   # Security & cost analysis
│   ├── scan_results/        # Old scan results
│   ├── tests/               # Test scripts
│   ├── legacy/              # Legacy files
│   ├── github/              # GitHub setup
│   └── README.md            # Archive index
│
└── 📁 node_modules/          # Node.js packages (gitignored)
```

---

## 📊 File Count Summary

| Directory | Files | Purpose |
|-----------|-------|---------|
| **Root** | 6 | Core configuration files |
| **lambda/** | 5 | Serverless functions |
| **scanners/** | 5 | AWS scanners |
| **policies/** | 35+ | OPA rules |
| **webapp/** | 50+ | Full web application |
| **scripts/** | 7 | Utility scripts |
| **config/** | 2 | Configuration files |
| **tests/** | 2 | Test files |
| **docs/** | 2 | Quick docs |
| **context_files/** | 30+ | Full documentation |

**Total**: ~150 files (organized)

---

## 🎯 Key Directories Explained

### Core Application (`/`)
- **serverless.yml**: Defines AWS infrastructure
- **package.json**: Node.js project configuration
- **requirements.txt**: Python dependencies

### Lambda Functions (`lambda/`)
- **API Handler**: Wraps FastAPI for Lambda
- **Workers**: Background job processors
- **Layers**: Shared dependencies

### Scanners (`scanners/`)
- **Modular Design**: Each scanner is independent
- **Base Class**: Common functionality
- **AWS Integration**: Uses boto3 for AWS API calls

### Policies (`policies/`)
- **OPA Rules**: Policy-as-code implementation
- **ISO Standards**: Mapped to technical controls
- **35+ Rules**: Comprehensive coverage

### Web Application (`webapp/`)
- **Backend**: FastAPI + PostgreSQL
- **Frontend**: React + TypeScript + Vite
- **Database**: Schema definitions

### Scripts (`scripts/`)
- **Local Development**: Quick start scripts
- **CLI Tools**: Scanner utilities
- **Organization**: Maintenance scripts

### Configuration (`config/`)
- **Environment-specific**: Different configs per environment
- **Serverless Settings**: Offline development config

### Tests (`tests/`)
- **Test Database**: SQLite for local testing
- **Test Scripts**: Validation utilities

### Documentation (`docs/`)
- **Quick Reference**: Essential docs for development
- **Local Info**: Server running information

### Context Files (`context_files/`)
- **Complete Archive**: All project documentation
- **Organized by Type**: Easy to find information
- **30+ Documents**: Comprehensive coverage

---

## 🚀 Quick Start Paths

### Run Local Development
```bash
# Backend API
python3 scripts/local/run_local_app.py

# Frontend
cd webapp/frontend && npm run dev
```

### Run Scanners
```bash
python3 scripts/scan_all.py --region us-east-1
```

### Deploy to AWS
```bash
serverless deploy --stage prod
```

### View Documentation
```bash
# Quick docs
cat docs/LOCAL_RUNNING.md

# Full documentation
ls context_files/
```

---

## 📝 File Naming Conventions

### Python Files
- **Snake_case**: `base_scanner.py`
- **Descriptive**: `sagemaker_scanner.py`

### TypeScript/React
- **PascalCase**: Components (`Dashboard.tsx`)
- **camelCase**: Utilities (`authStore.ts`)

### Documentation
- **UPPERCASE**: Important docs (`README.md`)
- **Title_Case**: Guides (`LOCAL_RUNNING.md`)

### Configuration
- **Kebab-case**: Config files (`serverless-local.yml`)

---

## 🔒 Security Considerations

### Gitignored Files
- `node_modules/` - Dependencies
- `*.db` - Databases
- `*.log` - Log files
- `.env*` - Environment variables
- `*.zip` - Deployment packages

### Sensitive Data
- **Never Commit**: Credentials, API keys
- **Use Secrets Manager**: For production
- **Environment Variables**: For local development

---

## 🎨 Organization Benefits

### Clean Root Directory
✅ Only essential files in root  
✅ Easy to understand structure  
✅ Professional appearance  

### Logical Grouping
✅ Scripts together  
✅ Config separated  
✅ Tests isolated  
✅ Docs accessible  

### Easy Navigation
✅ Clear folder names  
✅ README in each directory  
✅ Consistent structure  

### Deployment Ready
✅ Clean for CI/CD  
✅ Docker-friendly  
✅ Serverless-optimized  

---

## 📚 Related Documentation

- **Project Context**: `context_files/security_analysis/CONVERSATION_CONTEXT.md`
- **Deployment Guide**: `context_files/deployment/SERVERLESS_DEPLOYMENT.md`
- **Cost Analysis**: `context_files/security_analysis/COST_ANALYSIS.md`
- **Migration Guide**: `context_files/deployment/SERVERLESS_MIGRATION_GUIDE.md`

---

## ✅ Organization Status

**Status**: ✅ **COMPLETE**  
**Folders**: 13 organized directories  
**Files**: ~150 files properly categorized  
**Documentation**: Comprehensive README files  
**Clean**: No clutter in root directory  

---

**The project is now professionally organized and ready for development or deployment!** 🎉
