# AWS AI Governance Framework - Serverless Edition

**Cost-optimized serverless architecture using Lambda, Aurora Serverless v2, and DynamoDB**

## 🎯 Architecture

This is the **serverless version** of the AWS AI Governance Framework, optimized for:
- 60% cost savings ($55/month vs $138/month)
- Automatic scaling
- Pay-per-use pricing
- Zero server management

### Key Differences from Original

| Component | Original (ECS) | Serverless |
|-----------|----------------|------------|
| **API** | ECS Fargate (24/7) | Lambda + API Gateway |
| **Workers** | Celery on ECS | Lambda + SQS |
| **Database** | RDS Multi-AZ | Aurora Serverless v2 |
| **Cache** | ElastiCache Redis | DynamoDB |
| **Load Balancer** | ALB | API Gateway |
| **Cost** | $138/month | $55/month |

## 🚀 Quick Start

### Prerequisites
```bash
# Install Serverless Framework
npm install -g serverless

# Install plugins
npm install --save-dev serverless-python-requirements serverless-offline

# Configure AWS credentials
aws configure
```

### Deploy

```bash
# Deploy to AWS
serverless deploy --stage prod

# Output will show:
# - API Gateway URL
# - SQS Queue URL
# - DynamoDB Table name
# - S3 Results bucket
```

### Test

```bash
# Invoke API
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/health

# Trigger a scan
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"scan_type": "s3", "region": "us-east-1"}'

# Check logs
serverless logs -f scanner --tail
```

## 📊 Cost Breakdown

**Monthly Cost: ~$55**

| Service | Cost |
|---------|------|
| Lambda (API) | $5 |
| Lambda (Workers) | $2 |
| API Gateway | $3.50 |
| Aurora Serverless v2 | $15 |
| DynamoDB | $3 |
| SQS | $0.50 |
| S3 | $1 |
| CloudWatch | $7 |
| Other | $18 |

## 📚 Documentation

- `MIGRATION_APPLIED.md` - List of changes made during migration
- `SERVERLESS_DEPLOYMENT.md` - Detailed deployment guide
- `CONVERSATION_CONTEXT.md` - Full context from original project
- `COST_ANALYSIS.md` - Detailed cost comparison

## 🔄 Updating

```bash
# Update code
serverless deploy function -f api

# Update infrastructure
serverless deploy
```

## 🧪 Local Development

```bash
# Run locally with serverless-offline
serverless offline

# Test locally
curl http://localhost:3000/health
```

## 📝 Original Project

This is a serverless migration of the original ECS Fargate version.

**Original**: `/Volumes/Extreme SSD/repos/grc_ai_privacy`  
**Serverless**: `/Volumes/Extreme SSD/repos/grc_ai_privacy_serverless`

See `MIGRATION_APPLIED.md` for complete list of changes.
