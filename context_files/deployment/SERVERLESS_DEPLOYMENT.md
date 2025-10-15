# Serverless Deployment Guide

**Deploy the AWS AI Governance Framework using Lambda and Aurora Serverless v2**

**Estimated Time**: 30-45 minutes  
**Estimated Cost**: $55/month  
**Downtime**: Zero

---

## 🎯 Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Set environment variables
export AURORA_CLUSTER_ARN="arn:aws:rds:us-east-1:ACCOUNT:cluster:grc-aurora"
export AURORA_SECRET_ARN="arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:grc-db"

# 3. Deploy
serverless deploy --stage prod

# 4. Test
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/health
```

---

## 📋 Prerequisites

### Required
- ✅ AWS Account with admin access
- ✅ AWS CLI configured (`aws configure`)
- ✅ Node.js 18+ installed
- ✅ Python 3.9+ installed
- ✅ ~$55/month budget

### Optional
- Docker (for local testing)
- Git (for version control)

---

## 🚀 Step-by-Step Deployment

### Step 1: Install Serverless Framework (5 minutes)

```bash
# Install globally
npm install -g serverless

# Verify installation
serverless --version
# Should show: Framework Core: 3.38.0 or higher

# Install project dependencies
cd /Volumes/Extreme\ SSD/repos/grc_ai_privacy_serverless
npm install
```

**Expected output**:
```
added 150 packages in 30s
```

---

### Step 2: Create Aurora Serverless v2 Cluster (10 minutes)

```bash
# Set variables
export AWS_REGION=us-east-1
export DB_PASSWORD=$(openssl rand -base64 32)

# Create DB subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name grc-db-subnet-group \
  --db-subnet-group-description "Subnet group for GRC database" \
  --subnet-ids subnet-xxx subnet-yyy \
  --region $AWS_REGION

# Create Aurora Serverless v2 cluster
aws rds create-db-cluster \
  --db-cluster-identifier grc-aurora-serverless \
  --engine aurora-postgresql \
  --engine-version 15.4 \
  --master-username grc_admin \
  --master-user-password "$DB_PASSWORD" \
  --database-name grc_governance \
  --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=2 \
  --enable-http-endpoint \
  --vpc-security-group-ids sg-xxx \
  --db-subnet-group-name grc-db-subnet-group \
  --region $AWS_REGION

# Create Aurora Serverless v2 instance
aws rds create-db-instance \
  --db-instance-identifier grc-aurora-serverless-instance \
  --db-instance-class db.serverless \
  --engine aurora-postgresql \
  --db-cluster-identifier grc-aurora-serverless \
  --region $AWS_REGION

# Wait for cluster to be available (5-10 minutes)
aws rds wait db-cluster-available \
  --db-cluster-identifier grc-aurora-serverless \
  --region $AWS_REGION

echo "Aurora cluster created successfully!"
```

**Get cluster ARN**:
```bash
export AURORA_CLUSTER_ARN=$(aws rds describe-db-clusters \
  --db-cluster-identifier grc-aurora-serverless \
  --query 'DBClusters[0].DBClusterArn' \
  --output text \
  --region $AWS_REGION)

echo "Cluster ARN: $AURORA_CLUSTER_ARN"
```

---

### Step 3: Store Database Credentials (5 minutes)

```bash
# Create secret in Secrets Manager
aws secretsmanager create-secret \
  --name grc/database \
  --description "GRC database credentials" \
  --secret-string "{
    \"username\": \"grc_admin\",
    \"password\": \"$DB_PASSWORD\",
    \"engine\": \"postgres\",
    \"host\": \"$(aws rds describe-db-clusters --db-cluster-identifier grc-aurora-serverless --query 'DBClusters[0].Endpoint' --output text)\",
    \"port\": 5432,
    \"dbname\": \"grc_governance\"
  }" \
  --region $AWS_REGION

# Get secret ARN
export AURORA_SECRET_ARN=$(aws secretsmanager describe-secret \
  --secret-id grc/database \
  --query 'ARN' \
  --output text \
  --region $AWS_REGION)

echo "Secret ARN: $AURORA_SECRET_ARN"
```

**Save these values** - you'll need them for deployment!

---

### Step 4: Deploy Serverless Application (10 minutes)

```bash
# Set environment variables
export AURORA_CLUSTER_ARN="<your-cluster-arn>"
export AURORA_SECRET_ARN="<your-secret-arn>"

# Deploy to production
serverless deploy --stage prod --region us-east-1

# This will:
# 1. Package Lambda functions
# 2. Create S3 bucket for deployment artifacts
# 3. Upload code to S3
# 4. Create CloudFormation stack
# 5. Deploy API Gateway, Lambda, DynamoDB, SQS
# 6. Set up IAM roles and permissions
```

**Expected output**:
```
Deploying grc-ai-governance to stage prod (us-east-1)

✔ Service deployed to stack grc-ai-governance-prod (112s)

endpoints:
  ANY - https://abc123xyz.execute-api.us-east-1.amazonaws.com/{proxy+}
functions:
  api: grc-ai-governance-prod-api (15 MB)
  scanner: grc-ai-governance-prod-scanner (15 MB)
  scheduledScan: grc-ai-governance-prod-scheduledScan (15 MB)
```

**Save the API endpoint URL!**

---

### Step 5: Initialize Database Schema (5 minutes)

```bash
# Get API URL from deployment output
export API_URL="https://abc123xyz.execute-api.us-east-1.amazonaws.com"

# Initialize database (creates tables)
curl -X POST $API_URL/api/v1/admin/init-db \
  -H "Content-Type: application/json"

# Expected response:
# {"status": "success", "message": "Database initialized"}
```

---

### Step 6: Test Deployment (5 minutes)

```bash
# Test health endpoint
curl $API_URL/health

# Expected response:
# {"status":"healthy","version":"1.0.0","environment":"production"}

# Test scanner endpoint
curl -X POST $API_URL/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{
    "scan_type": "s3",
    "region": "us-east-1"
  }'

# Expected response:
# {"status":"queued","job_id":"xxx","message":"Scan job queued"}

# Check logs
serverless logs -f scanner --tail --stage prod
```

---

## 📊 Verify Deployment

### Check All Resources

```bash
# List Lambda functions
aws lambda list-functions \
  --query 'Functions[?contains(FunctionName, `grc-ai-governance`)].FunctionName' \
  --output table

# Check API Gateway
aws apigatewayv2 get-apis \
  --query 'Items[?contains(Name, `grc-ai-governance`)].{Name:Name,ApiEndpoint:ApiEndpoint}' \
  --output table

# Check DynamoDB table
aws dynamodb describe-table \
  --table-name grc-ai-governance-prod-cache \
  --query 'Table.{Name:TableName,Status:TableStatus,ItemCount:ItemCount}'

# Check SQS queue
aws sqs get-queue-url \
  --queue-name grc-ai-governance-prod-scan-queue

# Check S3 bucket
aws s3 ls | grep grc-ai-governance

# Check Aurora cluster
aws rds describe-db-clusters \
  --db-cluster-identifier grc-aurora-serverless \
  --query 'DBClusters[0].{Status:Status,Endpoint:Endpoint,Engine:Engine}'
```

---

## 🧪 Testing

### Manual Testing

```bash
# 1. Health check
curl $API_URL/health

# 2. Trigger S3 scan
curl -X POST $API_URL/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"scan_type": "s3", "region": "us-east-1"}'

# 3. Trigger SageMaker scan
curl -X POST $API_URL/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"scan_type": "sagemaker", "region": "us-east-1"}'

# 4. Get scan results
curl $API_URL/api/v1/scans

# 5. Check dashboard
curl $API_URL/api/v1/dashboard/overview
```

### Load Testing

```bash
# Install artillery
npm install -g artillery

# Create load test
cat > load-test.yml << EOF
config:
  target: '$API_URL'
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - flow:
      - get:
          url: '/health'
      - post:
          url: '/api/v1/scan'
          json:
            scan_type: 's3'
            region: 'us-east-1'
EOF

# Run load test
artillery run load-test.yml
```

---

## 📈 Monitoring

### CloudWatch Logs

```bash
# View API logs
serverless logs -f api --tail --stage prod

# View scanner logs
serverless logs -f scanner --tail --stage prod

# View scheduled scan logs
serverless logs -f scheduledScan --tail --stage prod
```

### CloudWatch Metrics

```bash
# Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=grc-ai-governance-prod-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Lambda errors
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=grc-ai-governance-prod-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Lambda duration
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=grc-ai-governance-prod-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

---

## 💰 Cost Monitoring

### Set Up Budget Alert

```bash
# Create budget
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget '{
    "BudgetName": "GRC-Serverless-Monthly",
    "BudgetLimit": {
      "Amount": "60",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }' \
  --notifications-with-subscribers '[
    {
      "Notification": {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 80
      },
      "Subscribers": [
        {
          "SubscriptionType": "EMAIL",
          "Address": "your-email@example.com"
        }
      ]
    }
  ]'
```

### Check Current Costs

```bash
# Get cost for last 7 days
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '7 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=SERVICE \
  --filter '{
    "Tags": {
      "Key": "Project",
      "Values": ["grc-ai-governance"]
    }
  }'
```

---

## 🔄 Updates & Maintenance

### Update Lambda Function

```bash
# Update single function
serverless deploy function -f api --stage prod

# Update all functions
serverless deploy --stage prod
```

### Update Environment Variables

```bash
# Update serverless.yml, then:
serverless deploy --stage prod
```

### View Deployment Info

```bash
# Get deployment details
serverless info --stage prod

# Get function details
serverless info --function api --stage prod
```

---

## 🆘 Troubleshooting

### Lambda Function Not Working

```bash
# Check function logs
serverless logs -f api --tail --stage prod

# Invoke function directly
serverless invoke -f api --stage prod --data '{
  "path": "/health",
  "httpMethod": "GET"
}'

# Check function configuration
aws lambda get-function-configuration \
  --function-name grc-ai-governance-prod-api
```

### Database Connection Issues

```bash
# Test Data API connection
aws rds-data execute-statement \
  --resource-arn $AURORA_CLUSTER_ARN \
  --secret-arn $AURORA_SECRET_ARN \
  --database grc_governance \
  --sql "SELECT 1"

# Check cluster status
aws rds describe-db-clusters \
  --db-cluster-identifier grc-aurora-serverless \
  --query 'DBClusters[0].Status'
```

### API Gateway Issues

```bash
# Get API details
aws apigatewayv2 get-apis \
  --query 'Items[?contains(Name, `grc-ai-governance`)]'

# Check API stages
aws apigatewayv2 get-stages \
  --api-id <API_ID>
```

### High Costs

```bash
# Check Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=grc-ai-governance-prod-api \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum

# Check Aurora usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ServerlessDatabaseCapacity \
  --dimensions Name=DBClusterIdentifier,Value=grc-aurora-serverless \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average
```

---

## 🗑️ Cleanup / Removal

### Remove Serverless Deployment

```bash
# Remove all serverless resources
serverless remove --stage prod

# This will delete:
# - Lambda functions
# - API Gateway
# - DynamoDB tables
# - SQS queues
# - S3 buckets (if empty)
# - IAM roles
# - CloudWatch log groups
```

### Remove Aurora Cluster

```bash
# Delete Aurora instance
aws rds delete-db-instance \
  --db-instance-identifier grc-aurora-serverless-instance \
  --skip-final-snapshot

# Delete Aurora cluster
aws rds delete-db-cluster \
  --db-cluster-identifier grc-aurora-serverless \
  --skip-final-snapshot

# Delete secret
aws secretsmanager delete-secret \
  --secret-id grc/database \
  --force-delete-without-recovery
```

---

## ✅ Post-Deployment Checklist

### Day 1
- [ ] Verify all endpoints working
- [ ] Run test scans
- [ ] Check CloudWatch logs
- [ ] Verify database connections
- [ ] Test scheduled scans
- [ ] Set up monitoring alerts

### Week 1
- [ ] Monitor costs daily
- [ ] Review CloudWatch metrics
- [ ] Optimize Lambda memory/timeout
- [ ] Test error scenarios
- [ ] Document any issues
- [ ] Update team on status

### Month 1
- [ ] Review monthly costs
- [ ] Optimize based on usage patterns
- [ ] Update documentation
- [ ] Plan additional features
- [ ] Review security posture

---

## 📚 Additional Resources

- `README_SERVERLESS.md` - Quick start guide
- `MIGRATION_APPLIED.md` - Changes from original
- `CONVERSATION_CONTEXT.md` - Full project history
- `COST_ANALYSIS.md` - Cost breakdown
- `serverless.yml` - Infrastructure configuration

---

## 🎯 Success Criteria

✅ All Lambda functions deployed  
✅ API Gateway responding  
✅ Aurora cluster running  
✅ DynamoDB table created  
✅ SQS queue created  
✅ Health endpoint returns 200  
✅ Scans can be triggered  
✅ Results stored in S3  
✅ Costs under $60/month  
✅ No errors in CloudWatch logs  

---

**Deployment Time**: 30-45 minutes  
**Monthly Cost**: ~$55  
**Downtime**: Zero  
**Rollback Time**: 5 minutes (`serverless remove`)

**Ready to deploy? Follow the steps above!** 🚀
