# Quick Deploy Guide

**For experienced AWS users who want to deploy quickly**

---

## ⚡ 5-Minute Quick Start

### Prerequisites
- AWS CLI configured
- Docker installed
- Domain name (optional)
- ~$140/month budget

### Step 1: Set Variables (1 minute)
```bash
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export PROJECT_NAME=grc
export DOMAIN_NAME=grc.yourdomain.com  # Optional
```

### Step 2: Create ECR Repositories (1 minute)
```bash
aws ecr create-repository --repository-name ${PROJECT_NAME}-backend --region ${AWS_REGION}
aws ecr create-repository --repository-name ${PROJECT_NAME}-frontend --region ${AWS_REGION}
aws ecr create-repository --repository-name ${PROJECT_NAME}-celery-worker --region ${AWS_REGION}
```

### Step 3: Push Docker Images (2 minutes)
```bash
# Run the deployment script
./deploy.sh
```

### Step 4: Create Infrastructure (Automated)
```bash
# Use AWS Console Quick Create Stack or run:
# (Full instructions in AWS_DEPLOYMENT_GUIDE.md)

# For now, manually create:
# 1. VPC with public/private subnets
# 2. RDS PostgreSQL (db.t3.micro)
# 3. ElastiCache Redis (cache.t3.micro)
# 4. ECS Cluster
# 5. Application Load Balancer
```

### Step 5: Deploy Services (1 minute)
```bash
# Update task definitions with your values
sed -i '' "s/<ACCOUNT_ID>/${AWS_ACCOUNT_ID}/g" task-definitions/*.json

# Register and create services
aws ecs register-task-definition --cli-input-json file://task-definitions/backend-task-definition.json
aws ecs register-task-definition --cli-input-json file://task-definitions/celery-worker-task-definition.json

# Create services (after ALB and target groups are ready)
# See AWS_DEPLOYMENT_GUIDE.md for complete commands
```

---

## 🎯 What You Get

After deployment:
- ✅ Backend API on ECS Fargate
- ✅ Celery worker for background tasks
- ✅ PostgreSQL database (Multi-AZ)
- ✅ Redis cache
- ✅ Application Load Balancer
- ✅ CloudWatch logging
- ✅ Auto-scaling enabled

---

## 📊 Cost Breakdown

| Component | Monthly Cost |
|-----------|--------------|
| ECS Tasks | $45 |
| RDS PostgreSQL | $30 |
| ElastiCache Redis | $15 |
| Load Balancer | $20 |
| CloudFront | $5 |
| Other | $23 |
| **Total** | **~$138** |

---

## 🔧 Quick Commands

### Deploy Updates
```bash
./deploy.sh
```

### Check Status
```bash
aws ecs describe-services --cluster grc-cluster --services grc-backend-service
```

### View Logs
```bash
aws logs tail /ecs/grc-backend --follow
```

### Scale Services
```bash
aws ecs update-service --cluster grc-cluster --service grc-backend-service --desired-count 3
```

---

## 📝 Full Documentation

For complete step-by-step instructions, see:
- **AWS_DEPLOYMENT_GUIDE.md** - Complete deployment guide
- **PRE_DEPLOYMENT_DEBUG_REPORT.md** - System verification
- **README.md** - Project overview

---

## ⚠️ Important Notes

1. **Secrets**: Generate new SECRET_KEY before production
   ```bash
   openssl rand -hex 32
   ```

2. **Database**: Change default password in Secrets Manager

3. **SSL**: Configure ACM certificate for HTTPS

4. **Monitoring**: Set up CloudWatch alarms

5. **Backup**: Enable automated RDS backups

---

## 🆘 Need Help?

- Full guide: `AWS_DEPLOYMENT_GUIDE.md`
- Debug report: `PRE_DEPLOYMENT_DEBUG_REPORT.md`
- Local setup: `webapp/SETUP_GUIDE.md`

---

**Ready to deploy?** Start with `./deploy.sh` after creating ECR repositories!
