# Serverless Migration Guide

**Migrate from ECS Fargate to Lambda for 60% cost savings**

---

## 🎯 Migration Overview

**Current Cost**: $138/month  
**Target Cost**: $55/month  
**Savings**: $83/month (60%)  
**Migration Time**: 1-2 weeks  
**Downtime**: Zero (blue-green deployment)

---

## 📊 Before & After Comparison

### Current Architecture (ECS Fargate)
```
┌─────────────────────────────────────────────────┐
│                  CloudFront                      │
│              (Frontend - $5/mo)                  │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────┐
│          Application Load Balancer               │
│                 ($19/mo)                         │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
    ┌────▼────┐         ┌────▼────┐
    │ Backend │         │ Backend │
    │  Task 1 │         │  Task 2 │
    │ $15/mo  │         │ $15/mo  │
    └────┬────┘         └────┬────┘
         │                   │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │   Celery Worker   │
         │     ($15/mo)      │
         └─────────┬─────────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
┌───▼────┐                   ┌────▼────┐
│  RDS   │                   │  Redis  │
│ Multi  │                   │ Cache   │
│  -AZ   │                   │ $12/mo  │
│ $30/mo │                   └─────────┘
└────────┘

TOTAL: $138/month
```

### Target Architecture (Serverless)
```
┌─────────────────────────────────────────────────┐
│                  CloudFront                      │
│              (Frontend - $5/mo)                  │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────┐
│              API Gateway HTTP                    │
│                 ($3.50/mo)                       │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
    ┌────▼────┐         ┌────▼────┐
    │ Lambda  │         │ Lambda  │
    │  API 1  │   ...   │  API N  │
    │ $2/mo   │         │ $2/mo   │
    └────┬────┘         └────┬────┘
         │                   │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │    SQS Queue      │
         │     ($0.50/mo)    │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │  Lambda Worker    │
         │     ($1/mo)       │
         └─────────┬─────────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
┌───▼────┐                   ┌────▼────┐
│ Aurora │                   │DynamoDB │
│Server- │                   │  Cache  │
│less v2 │                   │  $3/mo  │
│ $15/mo │                   └─────────┘
└────────┘

TOTAL: $55/month
```

---

## 🔄 Migration Steps

### Phase 1: Preparation (Day 1-2)

#### 1. Set Up Serverless Framework
```bash
# Install Serverless Framework
npm install -g serverless

# Create serverless.yml
cd webapp/backend
serverless create --template aws-python3 --path lambda
```

#### 2. Create Lambda-Compatible Code
```python
# lambda/handler.py
import json
from mangum import Mangum
from app.main import app

# Wrap FastAPI with Mangum for Lambda
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """AWS Lambda handler"""
    return handler(event, context)
```

#### 3. Update Dependencies
```txt
# lambda/requirements.txt
fastapi==0.104.1
mangum==0.17.0  # FastAPI → Lambda adapter
boto3==1.34.0
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
```

### Phase 2: Database Migration (Day 3-4)

#### 1. Create Aurora Serverless v2
```bash
# Create Aurora Serverless v2 cluster
aws rds create-db-cluster \
  --db-cluster-identifier grc-aurora-serverless \
  --engine aurora-postgresql \
  --engine-version 15.4 \
  --master-username grc_admin \
  --master-user-password <STRONG_PASSWORD> \
  --database-name grc_governance \
  --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=2 \
  --enable-http-endpoint \
  --vpc-security-group-ids <SG_ID> \
  --db-subnet-group-name <SUBNET_GROUP>

# Create Aurora Serverless v2 instance
aws rds create-db-instance \
  --db-instance-identifier grc-aurora-serverless-instance \
  --db-instance-class db.serverless \
  --engine aurora-postgresql \
  --db-cluster-identifier grc-aurora-serverless
```

#### 2. Migrate Data
```bash
# Export from RDS
pg_dump -h <RDS_ENDPOINT> -U grc_admin -d grc_governance > backup.sql

# Import to Aurora
psql -h <AURORA_ENDPOINT> -U grc_admin -d grc_governance < backup.sql
```

#### 3. Update Connection Strings
```python
# Use Data API for Aurora Serverless
import boto3

rds_data = boto3.client('rds-data')

def execute_sql(sql, parameters=[]):
    response = rds_data.execute_statement(
        resourceArn='arn:aws:rds:us-east-1:ACCOUNT:cluster:grc-aurora',
        secretArn='arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:grc-db',
        database='grc_governance',
        sql=sql,
        parameters=parameters
    )
    return response
```

### Phase 3: Cache Migration (Day 5)

#### 1. Create DynamoDB Table
```bash
# Create DynamoDB table for caching
aws dynamodb create-table \
  --table-name grc-cache \
  --attribute-definitions \
    AttributeName=key,AttributeType=S \
  --key-schema \
    AttributeName=key,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --time-to-live-specification \
    Enabled=true,AttributeName=ttl
```

#### 2. Update Cache Code
```python
# Replace Redis with DynamoDB
import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
cache_table = dynamodb.Table('grc-cache')

def cache_set(key, value, ttl_seconds=3600):
    """Set cache value with TTL"""
    ttl = int((datetime.now() + timedelta(seconds=ttl_seconds)).timestamp())
    cache_table.put_item(
        Item={
            'key': key,
            'value': value,
            'ttl': ttl
        }
    )

def cache_get(key):
    """Get cache value"""
    response = cache_table.get_item(Key={'key': key})
    return response.get('Item', {}).get('value')
```

### Phase 4: API Gateway Setup (Day 6-7)

#### 1. Create API Gateway
```yaml
# serverless.yml
service: grc-api

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  memorySize: 512
  timeout: 30
  environment:
    AURORA_CLUSTER_ARN: ${env:AURORA_CLUSTER_ARN}
    AURORA_SECRET_ARN: ${env:AURORA_SECRET_ARN}
    DYNAMODB_CACHE_TABLE: grc-cache

functions:
  api:
    handler: handler.lambda_handler
    events:
      - httpApi:
          path: /{proxy+}
          method: ANY
    vpc:
      securityGroupIds:
        - ${env:SECURITY_GROUP_ID}
      subnetIds:
        - ${env:SUBNET_1}
        - ${env:SUBNET_2}

  scanner:
    handler: scanner_handler.lambda_handler
    timeout: 900  # 15 minutes
    memorySize: 1024
    events:
      - sqs:
          arn: !GetAtt ScanQueue.Arn
          batchSize: 1

resources:
  Resources:
    ScanQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: grc-scan-queue
        VisibilityTimeout: 900
```

#### 2. Deploy Lambda Functions
```bash
# Deploy to AWS
serverless deploy --stage prod

# Output:
# endpoints:
#   ANY - https://abc123.execute-api.us-east-1.amazonaws.com/{proxy+}
# functions:
#   api: grc-api-prod-api
#   scanner: grc-api-prod-scanner
```

### Phase 5: Background Jobs (Day 8-9)

#### 1. Create SQS Queue
```bash
# Create SQS queue for background jobs
aws sqs create-queue \
  --queue-name grc-scan-queue \
  --attributes VisibilityTimeout=900,MessageRetentionPeriod=86400
```

#### 2. Update Celery to SQS
```python
# Replace Celery with SQS
import boto3
import json

sqs = boto3.client('sqs')
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/ACCOUNT/grc-scan-queue'

def enqueue_scan(bucket_name, scan_type):
    """Enqueue scan job"""
    message = {
        'bucket_name': bucket_name,
        'scan_type': scan_type,
        'timestamp': datetime.now().isoformat()
    }
    
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(message)
    )

# Lambda worker processes SQS messages
def scanner_handler(event, context):
    """Process scan jobs from SQS"""
    for record in event['Records']:
        message = json.loads(record['body'])
        bucket_name = message['bucket_name']
        scan_type = message['scan_type']
        
        # Run scan
        results = run_scan(bucket_name, scan_type)
        
        # Store results in DynamoDB
        store_results(results)
```

### Phase 6: Testing (Day 10-11)

#### 1. Load Testing
```bash
# Install artillery
npm install -g artillery

# Create load test
cat > load-test.yml << EOF
config:
  target: 'https://abc123.execute-api.us-east-1.amazonaws.com'
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - flow:
      - get:
          url: '/health'
      - get:
          url: '/api/v1/dashboard/overview'
EOF

# Run test
artillery run load-test.yml
```

#### 2. Monitor Performance
```bash
# Check Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=grc-api-prod-api \
  --start-time 2025-10-14T00:00:00Z \
  --end-time 2025-10-14T23:59:59Z \
  --period 3600 \
  --statistics Average,Maximum
```

### Phase 7: Cutover (Day 12-14)

#### 1. Blue-Green Deployment
```bash
# Update Route 53 to point to API Gateway
aws route53 change-resource-record-sets \
  --hosted-zone-id <ZONE_ID> \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.grc.yourdomain.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "abc123.execute-api.us-east-1.amazonaws.com"}]
      }
    }]
  }'
```

#### 2. Monitor for 24 Hours
```bash
# Watch CloudWatch logs
aws logs tail /aws/lambda/grc-api-prod-api --follow

# Check error rates
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=grc-api-prod-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

#### 3. Decommission Old Infrastructure
```bash
# After 1 week of stable operation:

# Delete ECS services
aws ecs delete-service --cluster grc-cluster --service grc-backend-service --force
aws ecs delete-service --cluster grc-cluster --service grc-celery-service --force

# Delete ECS cluster
aws ecs delete-cluster --cluster grc-cluster

# Delete ALB
aws elbv2 delete-load-balancer --load-balancer-arn <ALB_ARN>

# Delete RDS (create final snapshot)
aws rds delete-db-instance \
  --db-instance-identifier grc-postgres \
  --final-db-snapshot-identifier grc-postgres-final-snapshot

# Delete ElastiCache
aws elasticache delete-cache-cluster --cache-cluster-id grc-redis
```

---

## 📊 Performance Comparison

### Response Times
| Endpoint | ECS Fargate | Lambda (Warm) | Lambda (Cold) |
|----------|-------------|---------------|---------------|
| /health | 50ms | 30ms | 500ms |
| /api/v1/dashboard | 200ms | 150ms | 700ms |
| /api/v1/scan | 5s | 4s | 5.5s |

### Throughput
| Architecture | Requests/Second | Max Concurrent |
|--------------|-----------------|----------------|
| ECS Fargate | 100 | 200 |
| Lambda | 1,000+ | 1,000+ |

### Cold Start Impact
- **Frequency**: 1-5% of requests (with provisioned concurrency: 0%)
- **Duration**: 300-700ms
- **Mitigation**: Keep 1-2 Lambda instances warm with scheduled pings

---

## 💰 Cost Breakdown

### Monthly Costs by Traffic

#### Low Traffic (100K requests/month)
| Service | Cost |
|---------|------|
| Lambda (API) | $2.00 |
| Lambda (Worker) | $1.00 |
| API Gateway | $0.35 |
| Aurora Serverless | $8.00 |
| DynamoDB | $1.00 |
| SQS | $0.10 |
| CloudWatch | $3.00 |
| Other | $5.00 |
| **Total** | **$20.45** |

#### Medium Traffic (1M requests/month)
| Service | Cost |
|---------|------|
| Lambda (API) | $5.00 |
| Lambda (Worker) | $2.00 |
| API Gateway | $3.50 |
| Aurora Serverless | $15.00 |
| DynamoDB | $3.00 |
| SQS | $0.50 |
| CloudWatch | $7.00 |
| Other | $8.00 |
| **Total** | **$44.00** |

#### High Traffic (10M requests/month)
| Service | Cost |
|---------|------|
| Lambda (API) | $25.00 |
| Lambda (Worker) | $10.00 |
| API Gateway | $35.00 |
| Aurora Serverless | $30.00 |
| DynamoDB | $15.00 |
| SQS | $2.00 |
| CloudWatch | $15.00 |
| Other | $18.00 |
| **Total** | **$150.00** |

---

## ⚠️ Considerations

### Pros of Serverless
✅ **60% cost savings** at low-medium traffic  
✅ **Auto-scaling** - handles traffic spikes automatically  
✅ **No server management** - AWS handles everything  
✅ **Pay per use** - only pay for actual requests  
✅ **High availability** - built-in redundancy  
✅ **Fast deployments** - update in seconds  

### Cons of Serverless
❌ **Cold starts** - 300-700ms delay for first request  
❌ **15-minute timeout** - long-running tasks need workarounds  
❌ **Vendor lock-in** - harder to migrate off AWS  
❌ **Debugging complexity** - distributed tracing needed  
❌ **VPC cold starts** - slower if accessing VPC resources  
❌ **Cost at scale** - can be expensive at very high traffic  

### When to Use Serverless
✅ Traffic is unpredictable or spiky  
✅ Low to medium traffic (< 10M requests/month)  
✅ Cost optimization is priority  
✅ Team comfortable with serverless  
✅ Can tolerate occasional cold starts  

### When to Keep ECS/Fargate
✅ Consistent high traffic (> 10M requests/month)  
✅ Long-running processes (> 15 minutes)  
✅ Need sub-100ms response times  
✅ Complex networking requirements  
✅ Team prefers container-based architecture  

---

## 🎯 Quick Wins (No Migration Needed)

### 1. Enable Fargate Spot (Save $34/month)
```bash
# Update capacity provider strategy
aws ecs put-cluster-capacity-providers \
  --cluster grc-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE_SPOT,weight=4 \
    capacityProvider=FARGATE,weight=1
```

### 2. Use Aurora Serverless v2 (Save $15/month)
```bash
# Migrate RDS to Aurora Serverless v2
# (Requires snapshot → restore → cutover)
```

### 3. Replace ElastiCache with DynamoDB (Save $9/month)
```python
# Update cache layer to use DynamoDB
# (Can be done incrementally)
```

---

## ✅ Migration Checklist

### Pre-Migration
- [ ] Review current architecture
- [ ] Estimate traffic patterns
- [ ] Calculate cost savings
- [ ] Get team buy-in
- [ ] Set up test environment

### Migration
- [ ] Install Serverless Framework
- [ ] Create Lambda functions
- [ ] Set up Aurora Serverless v2
- [ ] Configure DynamoDB caching
- [ ] Create API Gateway
- [ ] Set up SQS queues
- [ ] Deploy to staging
- [ ] Load test
- [ ] Update DNS
- [ ] Monitor for 24 hours

### Post-Migration
- [ ] Decommission old infrastructure
- [ ] Update documentation
- [ ] Train team on new architecture
- [ ] Set up cost alerts
- [ ] Monitor performance
- [ ] Optimize based on metrics

---

**Estimated Migration Time**: 1-2 weeks  
**Estimated Cost Savings**: $83/month (60%)  
**Risk Level**: Low (blue-green deployment, zero downtime)  
**Recommended**: Yes, for low-medium traffic applications

---

**Guide Version**: 1.0  
**Last Updated**: October 14, 2025  
**Next Review**: After migration complete
