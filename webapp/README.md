# AWS AI Governance Web Application

Multi-tenant SaaS platform for AI/ML compliance monitoring with customizable dashboard views.

## 🏗️ Architecture

```
webapp/
├── frontend/          # React + TypeScript + Tailwind
├── backend/           # FastAPI + Python
├── database/          # PostgreSQL schemas
├── docker/            # Docker configurations
└── docs/              # Additional documentation
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15

### Development Setup

```bash
# Start all services with Docker Compose
docker-compose up -d

# Frontend will be available at: http://localhost:3000
# Backend API at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Manual Setup (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📊 Dashboard Views

The application supports 3 dashboard views (switchable in settings):

1. **Hybrid View** (Default) - Balanced for mixed teams
2. **Executive View** - High-level metrics for leadership
3. **Technical View** - Detailed findings for engineers

## 🔐 AWS Access Setup

See [AWS_SETUP.md](docs/AWS_SETUP.md) for cross-account IAM role configuration.

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [User Guide](docs/USER_GUIDE.md)

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📝 License

© 2025 AJ Williams - Portfolio Project
