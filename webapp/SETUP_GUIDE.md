# Web App Setup Guide

Complete guide to set up and run the AWS AI Governance Web Application.

## 📋 Prerequisites

### Required Software
- **Docker Desktop** 4.25+ (includes Docker Compose)
- **Node.js** 18+ and npm
- **Python** 3.11+
- **PostgreSQL** 15+ (or use Docker)
- **Git**

### Optional
- **AWS CLI** configured with credentials
- **OPA** binary for policy testing

---

## 🚀 Quick Start (Docker - Recommended)

### 1. Clone and Navigate
```bash
cd /path/to/grc_ai_privacy/webapp
```

### 2. Create Environment File
```bash
cat > backend/.env << EOF
DATABASE_URL=postgresql://grc_user:grc_password_dev@postgres:5432/grc_governance
REDIS_URL=redis://redis:6379/0
SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=development
EOF
```

### 3. Start All Services
```bash
docker-compose up -d
```

This starts:
- ✅ PostgreSQL database (port 5432)
- ✅ Redis (port 6379)
- ✅ FastAPI backend (port 8000)
- ✅ Celery worker
- ✅ React frontend (port 3000)

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 5. Create Initial User (First Time Only)
```bash
docker-compose exec backend python -m app.scripts.create_admin
```

Follow prompts to create admin user.

---

## 🛠️ Manual Setup (Without Docker)

### Backend Setup

#### 1. Create Virtual Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Set Up PostgreSQL
```bash
# Install PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb grc_governance
```

#### 4. Configure Environment
```bash
cat > .env << EOF
DATABASE_URL=postgresql://localhost:5432/grc_governance
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=development
EOF
```

#### 5. Run Database Migrations
```bash
# Initialize Alembic (first time only)
alembic init alembic

# Run migrations
alembic upgrade head
```

#### 6. Start Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

#### 1. Install Dependencies
```bash
cd frontend
npm install
```

#### 2. Configure Environment
```bash
cat > .env << EOF
VITE_API_URL=http://localhost:8000
EOF
```

#### 3. Start Development Server
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

### Redis Setup (for Celery)

```bash
# Install Redis (macOS)
brew install redis
brew services start redis

# Or run in Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Start Celery Worker

```bash
cd backend
celery -A app.tasks worker --loglevel=info
```

---

## 🗄️ Database Schema

The application uses the following main tables:

- **companies** - Multi-tenant organizations
- **users** - User accounts with roles
- **aws_accounts** - AWS account configurations
- **scans** - Scan execution records
- **findings** - Security findings
- **scan_schedules** - Scheduled scan configurations
- **dashboard_preferences** - User UI preferences

---

## 🔐 AWS Cross-Account Setup

### 1. Create IAM Role in Customer AWS Account

```bash
# Save this as trust-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::YOUR_SAAS_ACCOUNT:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "unique-customer-external-id"
        }
      }
    }
  ]
}

# Create role
aws iam create-role \
  --role-name GRCGovernanceScanner \
  --assume-role-policy-document file://trust-policy.json
```

### 2. Attach Read-Only Policy

```bash
# Save this as scanner-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:List*",
        "sagemaker:Describe*",
        "iam:List*",
        "iam:Get*",
        "s3:List*",
        "s3:GetBucket*"
      ],
      "Resource": "*"
    }
  ]
}

# Attach policy
aws iam put-role-policy \
  --role-name GRCGovernanceScanner \
  --policy-name ScannerReadOnly \
  --policy-document file://scanner-policy.json
```

### 3. Add AWS Account in Web App

1. Navigate to Settings → AWS Accounts
2. Click "Add AWS Account"
3. Enter:
   - Account ID: `123456789012`
   - Account Name: `Production`
   - Role ARN: `arn:aws:iam::123456789012:role/GRCGovernanceScanner`
   - External ID: `unique-customer-external-id`
   - Regions: `us-east-1, us-west-2`
4. Click "Test Connection" to verify
5. Save

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Start all services
docker-compose up -d

# Run integration tests
cd backend
pytest tests/integration/ -v
```

---

## 📊 Using the Dashboard

### Option 3: Hybrid Dashboard (Default)

The Hybrid Dashboard provides a balanced view with:

#### Top Section - Risk Overview
- **Risk Score**: 0-100 scale (weighted by severity)
- **Total Findings**: Count of all open findings
- **Compliance Rate**: Percentage of controls met
- **Last Scan**: Timestamp of most recent scan

#### Widget Grid (Customizable)
1. **Top Risks** - Most frequent issues
2. **Compliance Trends** - Historical chart
3. **AWS Accounts** - Account status and quick scan
4. **Recent Activity** - Latest scans and changes
5. **Control Coverage** - ISO framework compliance
6. **Remediation Progress** - Task status breakdown

#### Quick Findings List
- Priority findings requiring attention
- Quick actions (Fix, Assign, View Details)

### Switching Dashboard Views

1. Click user menu (top right)
2. Select "Dashboard Preferences"
3. Choose view:
   - **Hybrid** (Default) - Balanced
   - **Executive** - High-level metrics
   - **Technical** - Detailed findings
4. Save preferences

---

## 🔄 Running Scans

### Manual Scan
1. Navigate to Dashboard
2. Click "Run New Scan" button
3. Select AWS account and region
4. Click "Start Scan"
5. Monitor progress in Scans page

### Scheduled Scans
1. Navigate to Settings → Scan Schedules
2. Click "Add Schedule"
3. Configure:
   - AWS Account
   - Frequency (Daily/Weekly/Monthly)
   - Time
4. Save

Scans will run automatically via Celery worker.

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check database connection
docker-compose logs postgres

# Check backend logs
docker-compose logs backend

# Restart services
docker-compose restart backend
```

### Frontend won't connect to backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in backend/app/core/config.py
# Ensure frontend URL is in CORS_ORIGINS
```

### Database migrations fail
```bash
# Reset database (CAUTION: deletes all data)
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

### Scans not running
```bash
# Check Celery worker
docker-compose logs celery_worker

# Check Redis
docker-compose logs redis

# Restart Celery
docker-compose restart celery_worker
```

### AWS access denied
```bash
# Verify IAM role exists
aws iam get-role --role-name GRCGovernanceScanner

# Test assume role
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/GRCGovernanceScanner \
  --role-session-name test \
  --external-id unique-customer-external-id
```

---

## 📝 Development Workflow

### Making Backend Changes
1. Edit code in `backend/app/`
2. Backend auto-reloads (if using `--reload`)
3. Test at http://localhost:8000/docs

### Making Frontend Changes
1. Edit code in `frontend/src/`
2. Vite hot-reloads automatically
3. View at http://localhost:3000

### Database Schema Changes
1. Edit models in `backend/app/db/models.py`
2. Create migration:
   ```bash
   alembic revision --autogenerate -m "description"
   ```
3. Apply migration:
   ```bash
   alembic upgrade head
   ```

---

## 🚀 Deployment

### Production Checklist
- [ ] Change `SECRET_KEY` to strong random value
- [ ] Set `ENVIRONMENT=production`
- [ ] Use managed PostgreSQL (AWS RDS)
- [ ] Use managed Redis (AWS ElastiCache)
- [ ] Enable HTTPS/SSL
- [ ] Configure proper CORS origins
- [ ] Set up monitoring (CloudWatch, Sentry)
- [ ] Configure backups
- [ ] Set up CI/CD pipeline

### Deploy to AWS ECS
See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

---

## 📚 Additional Resources

- [API Documentation](http://localhost:8000/docs)
- [Database Schema](docs/DATABASE.md)
- [Architecture Guide](../WEB_APP_DASHBOARD_GUIDE.md)
- [User Guide](docs/USER_GUIDE.md)

---

## 🆘 Getting Help

1. Check logs: `docker-compose logs [service]`
2. Review API docs: http://localhost:8000/docs
3. Check database: `docker-compose exec postgres psql -U grc_user -d grc_governance`

---

**Ready to start?** Run `docker-compose up -d` and visit http://localhost:3000! 🎉
