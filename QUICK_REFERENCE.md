# Quick Reference Card

**Project**: GRC AI Governance Framework (Serverless)  
**Status**: Organized & Running

---

## Essential Commands

### Setup Environment
```bash
# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your AWS credentials
```

### Start Local Development
```bash
# Activate virtual environment
source venv/bin/activate

# Load environment variables
source .env

# Start serverless offline (API on port 3000)
npm start

# Alternative: Backend API directly (port 8001)
python3 scripts/local/run_local_app.py

# Frontend React (port 3001)
cd webapp/frontend && npm run dev
```

### Run Scanners
```bash
# All scanners
python3 scripts/scan_all.py --region us-east-1

# S3 only
python3 scripts/scan_all_buckets.py --region us-east-1
```

### Deploy to AWS
```bash
# Development
npm run deploy

# Production
npm run deploy:prod

# Remove deployment
npm run remove

# View logs
npm run logs
```

---

## Where to Find Things

| What | Where |
|------|-------|
| **Lambda functions** | `lambda/` |
| **Scanner modules** | `scanners/` |
| **OPA policies** | `policies/` |
| **Backend API** | `webapp/backend/` |
| **Frontend React** | `webapp/frontend/` |
| **Dev scripts** | `scripts/local/` |
| **Config files** | `config/` |
| **Test database** | `tests/` |

---

## Local URLs

| Service | URL |
|---------|-----|
| **Serverless Offline API** | http://localhost:3000 |
| **Backend API (direct)** | http://localhost:8001 |
| **API Docs** | http://localhost:8001/docs |
| **Frontend** | http://localhost:3001 |

---

## Project Stats

- **Total Files**: ~150
- **Core Directories**: 10
- **Lambda Functions**: 3
- **Scanner Modules**: 3
- **OPA Policies**: 35+
- **Documentation**: 30+ files

---

## Common Tasks

### Check Health
```bash
curl http://localhost:3000/health
```

### View API Docs
```bash
open http://localhost:8001/docs
```

### Run Tests
```bash
# Activate virtual environment first
source venv/bin/activate

# Run unit tests
pytest tests/ -v --cov=scanners

# Test OPA policies
opa test policies/ -v
```

### Security Audit
```bash
# Python packages
safety scan

# Node.js packages
npm audit

# Code security scan
bandit -r scanners/ lambda/ webapp/
```

### View Project Files
```bash
ls -la
```

### Clean Up
```bash
# Stop all servers
pkill -f uvicorn
pkill -f vite

# Remove test files
rm tests/*.db
```

---

## Documentation

- `README.md` - Main project documentation
- `DEPLOY_AWS_MANUAL.md` - AWS deployment guide
- `QUICK_REFERENCE.md` - This file

---

## Next Steps

1. **Development**: Make changes, auto-reload enabled
2. **Testing**: Run scanners on your AWS account
3. **Deployment**: Follow `DEPLOY_AWS_MANUAL.md`
4. **Production**: Configure Aurora Serverless v2

---

## Shortcuts

| Action | Command |
|--------|---------|
| **Activate venv** | `source venv/bin/activate` |
| **Start serverless** | `npm start` |
| **Start backend** | `python3 scripts/local/run_local_app.py` |
| **Start frontend** | `cd webapp/frontend && npm run dev` |
| **Deploy** | `npm run deploy` |
| **View logs** | `npm run logs` |
| **Run scanner** | `python scripts/scan_all.py --region us-east-1` |
| **Security audit** | `safety scan && npm audit` |

---

## Troubleshooting

### Port in use?
```bash
# Backend: Use different port
cd webapp/backend
uvicorn app.main:app --port 8002

# Frontend: Vite auto-selects next port
```

### Dependencies missing?
```bash
# Python (use virtual environment)
source venv/bin/activate
pip install -r requirements.txt
pip install -r webapp/backend/requirements.txt

# Node.js
npm install
cd webapp/frontend && npm install
```

### Python version issues?
```bash
# Check Python version (requires 3.11+)
python3.11 --version

# Recreate virtual environment with Python 3.11
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment variables not set?
```bash
# Copy example file
cp .env.example .env

# Edit with your values
vim .env

# Load environment variables
source .env
```

### Clean start?
```bash
# Remove all test data
rm -rf tests/*.db
rm -rf node_modules
rm -rf webapp/frontend/node_modules

# Reinstall
npm install
cd webapp/frontend && npm install
```

---

**Keep this handy for quick reference!**

## Python Version

**Required**: Python 3.11+  
**Current**: Python 3.11.14 (in venv)

## Key Dependencies

- boto3: 1.42.19
- botocore: 1.42.19
- black: 25.11.0
- bandit: 1.9.2
- jinja2: 3.1.6
- pandas: 2.3.3
- serverless: 3.38.0

All packages are secure and up to date.
