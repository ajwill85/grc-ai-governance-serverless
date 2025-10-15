# AWS Deployment Guide

**Project**: AWS AI Governance Framework  
**Date**: October 14, 2025  
**Status**: Ready for Production Deployment

---

## 🎯 Deployment Overview

This guide covers deploying the AWS AI Governance Framework to production AWS infrastructure using:
- **ECS Fargate** for containerized services
- **RDS PostgreSQL** for database
- **ElastiCache Redis** for caching
- **Application Load Balancer** for traffic distribution
- **CloudFront** for frontend CDN
- **S3** for static assets
- **Secrets Manager** for credentials
- **CloudWatch** for monitoring

---

## 📋 Pre-Deployment Checklist

### ✅ Local Testing Complete
- [x] All dependencies installed
- [x] Python 3.9.6 verified
- [x] AWS credentials configured (Account: 335380200154)
- [x] Docker services running (backend, frontend, postgres, redis)
- [x] Backend API healthy (http://localhost:8000/health)
- [x] Scanner modules tested and working
- [x] All imports successful

### ⏳ Production Preparation
- [ ] Generate production SECRET_KEY
- [ ] Create AWS IAM roles for ECS
- [ ] Set up RDS database
- [ ] Configure ElastiCache Redis
- [ ] Create ECR repositories
- [ ] Set up VPC and security groups
- [ ] Configure domain and SSL certificates
- [ ] Set up CloudWatch logging
- [ ] Create Secrets Manager entries

---

## 🏗️ Architecture: Production AWS Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                        CloudFront CDN                        │
│                    (Frontend Distribution)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴──────────┐
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌──────────────────┐
│   S3 Bucket     │    │  Application     │
│  (Static Site)  │    │  Load Balancer   │
└─────────────────┘    └────────┬─────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
         ┌──────────────────┐    ┌──────────────────┐
         │  ECS Fargate     │    │  ECS Fargate     │
         │  (Backend API)   │    │  (Celery Worker) │
         └────────┬─────────┘    └────────┬─────────┘
                  │                       │
         ┌────────┴───────────────────────┴────────┐
         │                                          │
         ▼                                          ▼
┌─────────────────┐                      ┌─────────────────┐
│  RDS PostgreSQL │                      │ ElastiCache     │
│  (Multi-AZ)     │                      │ Redis           │
└─────────────────┘                      └─────────────────┘
```

---

## 🚀 Deployment Steps

### Phase 1: Infrastructure Setup (30-45 minutes)

#### Step 1: Create VPC and Networking
```bash
# Create VPC with public and private subnets
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=grc-vpc}]'

# Create subnets (2 public, 2 private across 2 AZs)
# Public subnets: 10.0.1.0/24, 10.0.2.0/24
# Private subnets: 10.0.10.0/24, 10.0.11.0/24

# Create Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=grc-igw}]'

# Create NAT Gateways for private subnets
# Create route tables and associations
```

#### Step 2: Create Security Groups
```bash
# ALB Security Group (allow 80, 443)
aws ec2 create-security-group \
  --group-name grc-alb-sg \
  --description "Security group for GRC ALB" \
  --vpc-id <VPC_ID>

# ECS Security Group (allow from ALB)
aws ec2 create-security-group \
  --group-name grc-ecs-sg \
  --description "Security group for GRC ECS tasks" \
  --vpc-id <VPC_ID>

# RDS Security Group (allow from ECS)
aws ec2 create-security-group \
  --group-name grc-rds-sg \
  --description "Security group for GRC RDS" \
  --vpc-id <VPC_ID>

# Redis Security Group (allow from ECS)
aws ec2 create-security-group \
  --group-name grc-redis-sg \
  --description "Security group for GRC Redis" \
  --vpc-id <VPC_ID>
```

#### Step 3: Create RDS PostgreSQL Database
```bash
# Create DB subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name grc-db-subnet-group \
  --db-subnet-group-description "Subnet group for GRC database" \
  --subnet-ids subnet-xxx subnet-yyy

# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier grc-postgres \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username grc_admin \
  --master-user-password <GENERATE_STRONG_PASSWORD> \
  --allocated-storage 20 \
  --storage-type gp3 \
  --db-subnet-group-name grc-db-subnet-group \
  --vpc-security-group-ids <RDS_SG_ID> \
  --backup-retention-period 7 \
  --multi-az \
  --storage-encrypted \
  --no-publicly-accessible
```

#### Step 4: Create ElastiCache Redis
```bash
# Create cache subnet group
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name grc-cache-subnet-group \
  --cache-subnet-group-description "Subnet group for GRC cache" \
  --subnet-ids subnet-xxx subnet-yyy

# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id grc-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --cache-subnet-group-name grc-cache-subnet-group \
  --security-group-ids <REDIS_SG_ID>
```

#### Step 5: Store Secrets in Secrets Manager
```bash
# Generate strong SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)

# Create secret for database
aws secretsmanager create-secret \
  --name grc/database \
  --description "GRC database credentials" \
  --secret-string "{\"username\":\"grc_admin\",\"password\":\"<DB_PASSWORD>\",\"host\":\"<RDS_ENDPOINT>\",\"port\":5432,\"database\":\"grc_governance\"}"

# Create secret for application
aws secretsmanager create-secret \
  --name grc/application \
  --description "GRC application secrets" \
  --secret-string "{\"secret_key\":\"$SECRET_KEY\",\"environment\":\"production\"}"
```

---

### Phase 2: Container Setup (20-30 minutes)

#### Step 6: Create ECR Repositories
```bash
# Create repository for backend
aws ecr create-repository \
  --repository-name grc-backend \
  --image-scanning-configuration scanOnPush=true

# Create repository for frontend
aws ecr create-repository \
  --repository-name grc-frontend \
  --image-scanning-configuration scanOnPush=true

# Create repository for celery worker
aws ecr create-repository \
  --repository-name grc-celery-worker \
  --image-scanning-configuration scanOnPush=true
```

#### Step 7: Build and Push Docker Images
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd webapp/backend
docker build -t grc-backend .
docker tag grc-backend:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/grc-backend:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/grc-backend:latest

# Build and push frontend (production build)
cd ../frontend
docker build -f Dockerfile.prod -t grc-frontend .
docker tag grc-frontend:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/grc-frontend:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/grc-frontend:latest

# Build and push celery worker
docker tag grc-backend:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/grc-celery-worker:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/grc-celery-worker:latest
```

---

### Phase 3: ECS Deployment (30-45 minutes)

#### Step 8: Create ECS Cluster
```bash
aws ecs create-cluster \
  --cluster-name grc-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1 \
    capacityProvider=FARGATE_SPOT,weight=4
```

#### Step 9: Create IAM Roles
```bash
# ECS Task Execution Role (for pulling images, logging)
aws iam create-role \
  --role-name grc-ecs-execution-role \
  --assume-role-policy-document file://ecs-trust-policy.json

aws iam attach-role-policy \
  --role-name grc-ecs-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# ECS Task Role (for application permissions)
aws iam create-role \
  --role-name grc-ecs-task-role \
  --assume-role-policy-document file://ecs-trust-policy.json

# Attach policies for S3, SageMaker, IAM read access
```

#### Step 10: Create Task Definitions
See `task-definitions/` directory for:
- `backend-task-definition.json`
- `frontend-task-definition.json`
- `celery-worker-task-definition.json`

```bash
# Register backend task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definitions/backend-task-definition.json

# Register celery worker task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definitions/celery-worker-task-definition.json
```

#### Step 11: Create Application Load Balancer
```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name grc-alb \
  --subnets <PUBLIC_SUBNET_1> <PUBLIC_SUBNET_2> \
  --security-groups <ALB_SG_ID> \
  --scheme internet-facing \
  --type application

# Create target group for backend
aws elbv2 create-target-group \
  --name grc-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id <VPC_ID> \
  --target-type ip \
  --health-check-path /health

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn <ALB_ARN> \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=<TARGET_GROUP_ARN>
```

#### Step 12: Create ECS Services
```bash
# Create backend service
aws ecs create-service \
  --cluster grc-cluster \
  --service-name grc-backend-service \
  --task-definition grc-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<PRIVATE_SUBNET_1>,<PRIVATE_SUBNET_2>],securityGroups=[<ECS_SG_ID>],assignPublicIp=DISABLED}" \
  --load-balancers targetGroupArn=<TARGET_GROUP_ARN>,containerName=grc-backend,containerPort=8000

# Create celery worker service
aws ecs create-service \
  --cluster grc-cluster \
  --service-name grc-celery-service \
  --task-definition grc-celery-worker:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<PRIVATE_SUBNET_1>,<PRIVATE_SUBNET_2>],securityGroups=[<ECS_SG_ID>],assignPublicIp=DISABLED}"
```

---

### Phase 4: Frontend Deployment (15-20 minutes)

#### Step 13: Build Frontend for Production
```bash
cd webapp/frontend

# Update .env.production with ALB endpoint
echo "VITE_API_URL=http://<ALB_DNS_NAME>" > .env.production

# Build production bundle
npm run build

# Upload to S3
aws s3 sync dist/ s3://grc-frontend-<ACCOUNT_ID>/ --delete
```

#### Step 14: Create CloudFront Distribution
```bash
# Create S3 bucket for frontend
aws s3 mb s3://grc-frontend-<ACCOUNT_ID> --region us-east-1

# Configure bucket for static website hosting
aws s3 website s3://grc-frontend-<ACCOUNT_ID>/ \
  --index-document index.html \
  --error-document index.html

# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name grc-frontend-<ACCOUNT_ID>.s3-website-us-east-1.amazonaws.com \
  --default-root-object index.html
```

---

### Phase 5: Monitoring & Logging (10-15 minutes)

#### Step 15: Configure CloudWatch
```bash
# Create log groups
aws logs create-log-group --log-group-name /ecs/grc-backend
aws logs create-log-group --log-group-name /ecs/grc-celery-worker

# Set retention
aws logs put-retention-policy \
  --log-group-name /ecs/grc-backend \
  --retention-in-days 30
```

#### Step 16: Create CloudWatch Alarms
```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name grc-backend-high-cpu \
  --alarm-description "Alert when backend CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# High memory alarm
# Error rate alarm
# Database connection alarm
```

---

## 🔒 Security Hardening

### SSL/TLS Configuration
```bash
# Request ACM certificate
aws acm request-certificate \
  --domain-name grc.yourdomain.com \
  --validation-method DNS \
  --subject-alternative-names *.grc.yourdomain.com

# Update ALB listener to use HTTPS
aws elbv2 create-listener \
  --load-balancer-arn <ALB_ARN> \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=<ACM_CERT_ARN> \
  --default-actions Type=forward,TargetGroupArn=<TARGET_GROUP_ARN>
```

### WAF Configuration
```bash
# Create WAF Web ACL
aws wafv2 create-web-acl \
  --name grc-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://waf-rules.json

# Associate with ALB
aws wafv2 associate-web-acl \
  --web-acl-arn <WAF_ARN> \
  --resource-arn <ALB_ARN>
```

### Security Best Practices
- ✅ All traffic encrypted (TLS 1.2+)
- ✅ Secrets in Secrets Manager (not environment variables)
- ✅ Database in private subnet (no public access)
- ✅ Least privilege IAM roles
- ✅ Security groups with minimal ports
- ✅ WAF for DDoS protection
- ✅ CloudTrail for audit logging
- ✅ GuardDuty for threat detection

---

## 📊 Cost Estimation

### Monthly AWS Costs (Estimated)

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| **ECS Fargate** | 2 backend tasks (0.5 vCPU, 1GB) | ~$30 |
| **ECS Fargate** | 1 celery task (0.5 vCPU, 1GB) | ~$15 |
| **RDS PostgreSQL** | db.t3.micro Multi-AZ | ~$30 |
| **ElastiCache Redis** | cache.t3.micro | ~$15 |
| **Application Load Balancer** | Standard | ~$20 |
| **CloudFront** | 50GB transfer | ~$5 |
| **S3** | 10GB storage + requests | ~$2 |
| **Secrets Manager** | 2 secrets | ~$1 |
| **CloudWatch** | Logs + metrics | ~$10 |
| **Data Transfer** | Outbound | ~$10 |
| **Total** | | **~$138/month** |

### Cost Optimization
- Use Fargate Spot for non-critical tasks (70% savings)
- Use RDS Reserved Instances (40% savings)
- Enable S3 Intelligent-Tiering
- Set CloudWatch log retention to 30 days
- Use CloudFront caching aggressively

---

## 🧪 Testing Production Deployment

### Health Checks
```bash
# Test ALB health
curl https://grc.yourdomain.com/health

# Test API endpoints
curl https://grc.yourdomain.com/api/v1/dashboard/overview \
  -H "Authorization: Bearer <TOKEN>"

# Test frontend
curl https://grc.yourdomain.com/

# Check ECS task status
aws ecs describe-services \
  --cluster grc-cluster \
  --services grc-backend-service
```

### Load Testing
```bash
# Install Apache Bench
brew install httpd

# Run load test
ab -n 1000 -c 10 https://grc.yourdomain.com/health

# Monitor CloudWatch metrics during test
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push backend
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: grc-backend
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd webapp/backend
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      
      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster grc-cluster \
            --service grc-backend-service \
            --force-new-deployment
```

---

## 📝 Post-Deployment Checklist

### Immediate (Day 1)
- [ ] Verify all services healthy
- [ ] Test all API endpoints
- [ ] Verify frontend loads correctly
- [ ] Check CloudWatch logs for errors
- [ ] Test scanner functionality
- [ ] Verify database connections
- [ ] Test Redis caching
- [ ] Confirm SSL certificate valid

### Week 1
- [ ] Monitor CloudWatch metrics
- [ ] Review CloudWatch alarms
- [ ] Check cost explorer
- [ ] Test backup/restore procedures
- [ ] Verify auto-scaling works
- [ ] Load test production
- [ ] Security scan with AWS Inspector
- [ ] Review CloudTrail logs

### Month 1
- [ ] Review and optimize costs
- [ ] Tune auto-scaling policies
- [ ] Optimize database queries
- [ ] Review security groups
- [ ] Update documentation
- [ ] Implement additional monitoring
- [ ] Plan disaster recovery test

---

## 🆘 Troubleshooting

### Common Issues

#### ECS Tasks Not Starting
```bash
# Check task logs
aws logs tail /ecs/grc-backend --follow

# Check task stopped reason
aws ecs describe-tasks \
  --cluster grc-cluster \
  --tasks <TASK_ARN>
```

#### Database Connection Issues
```bash
# Test from ECS task
aws ecs execute-command \
  --cluster grc-cluster \
  --task <TASK_ID> \
  --container grc-backend \
  --interactive \
  --command "/bin/bash"

# Inside container
psql -h <RDS_ENDPOINT> -U grc_admin -d grc_governance
```

#### High Costs
```bash
# Check cost breakdown
aws ce get-cost-and-usage \
  --time-period Start=2025-10-01,End=2025-10-31 \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

---

## 📞 Support Resources

### AWS Documentation
- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [RDS Security](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.html)
- [CloudFront Distribution](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/)

### Project Documentation
- `README.md` - Project overview
- `webapp/SETUP_GUIDE.md` - Local development
- `SECURITY_AUDIT.md` - Security considerations
- `90_DAY_IMPLEMENTATION_PLAN.md` - Roadmap

---

## ✅ Deployment Complete!

Once deployed, your AWS AI Governance Framework will be:
- ✅ **Highly Available** - Multi-AZ deployment
- ✅ **Scalable** - Auto-scaling ECS tasks
- ✅ **Secure** - WAF, SSL, private subnets
- ✅ **Monitored** - CloudWatch metrics and alarms
- ✅ **Cost-Optimized** - Fargate Spot, right-sized instances
- ✅ **Production-Ready** - Automated deployments via CI/CD

**Next Steps**: Follow the deployment phases in order, testing each component before proceeding to the next.

**Estimated Total Deployment Time**: 2-3 hours

---

**Deployment Guide Version**: 1.0  
**Last Updated**: October 14, 2025  
**Maintained By**: AJ Williams
