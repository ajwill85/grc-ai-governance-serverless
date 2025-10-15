# 🚀 Quick Reference Card

**Project**: GRC AI Governance Framework (Serverless)  
**Status**: ✅ Organized & Running

---

## 📍 Essential Commands

### Start Local Development
```bash
# Backend API (port 8001)
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
serverless deploy --stage dev

# Production
serverless deploy --stage prod
```

---

## 📁 Where to Find Things

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
| **Quick docs** | `docs/` |
| **Full docs** | `context_files/` |

---

## 🌐 Local URLs

| Service | URL |
|---------|-----|
| **Backend API** | http://localhost:8001 |
| **API Docs** | http://localhost:8001/docs |
| **Frontend** | http://localhost:3001 |

---

## 📊 Project Stats

- **Total Files**: ~150
- **Core Directories**: 10
- **Lambda Functions**: 3
- **Scanner Modules**: 3
- **OPA Policies**: 35+
- **Documentation**: 30+ files

---

## 🔧 Common Tasks

### Check Health
```bash
curl http://localhost:8001/health
```

### View API Docs
```bash
open http://localhost:8001/docs
```

### Run Tests
```bash
python3 scripts/local/test_local.py
```

### View Structure
```bash
cat PROJECT_STRUCTURE.md
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

## 📚 Documentation Map

```
docs/                          # Quick reference
├── LOCAL_RUNNING.md          # Server info
├── ORGANIZATION_COMPLETE.md  # What was organized
└── README.md                 # Docs index

context_files/                 # Full documentation
├── deployment/               # How to deploy
├── project_docs/            # Project details
├── security_analysis/       # Security & costs
└── README.md               # Complete index
```

---

## 🎯 Next Steps

1. **Development**: Make changes, auto-reload enabled
2. **Testing**: Run scanners on your AWS account
3. **Deployment**: Follow `context_files/deployment/SERVERLESS_DEPLOYMENT.md`
4. **Production**: Configure Aurora Serverless v2

---

## ⚡ Shortcuts

| Action | Command |
|--------|---------|
| **Start backend** | `python3 scripts/local/run_local_app.py` |
| **Start frontend** | `cd webapp/frontend && npm run dev` |
| **Deploy** | `serverless deploy` |
| **View logs** | `serverless logs -f api --tail` |
| **Run scanner** | `python3 scripts/scan_all.py` |

---

## 🔍 Troubleshooting

### Port in use?
```bash
# Backend: Use different port
cd webapp/backend
uvicorn app.main:app --port 8002

# Frontend: Vite auto-selects next port
```

### Dependencies missing?
```bash
# Python
pip3 install -r requirements.txt
pip3 install -r webapp/backend/requirements.txt

# Node.js
npm install
cd webapp/frontend && npm install
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

**Keep this card handy for quick reference!** 📌
