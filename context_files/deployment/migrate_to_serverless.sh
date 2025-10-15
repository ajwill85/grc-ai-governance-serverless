#!/bin/bash

# AWS AI Governance Framework - Serverless Migration Script
# This script converts the ECS Fargate architecture to serverless

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Serverless Migration Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Step 1: Create Lambda directory structure
print_info "Creating Lambda directory structure..."
mkdir -p lambda/api
mkdir -p lambda/workers
mkdir -p lambda/layers/python
print_status "Lambda directories created"

# Step 2: Remove Docker-specific files
print_info "Removing Docker-specific files..."
rm -f webapp/docker-compose.yml
rm -f webapp/backend/Dockerfile
rm -f webapp/frontend/Dockerfile
rm -f webapp/frontend/Dockerfile.prod
rm -f deploy.sh
print_status "Docker files removed"

# Step 3: Create serverless.yml
print_info "Creating serverless.yml configuration..."
cat > serverless.yml << 'EOF'
service: grc-ai-governance

frameworkVersion: '3'

provider:
  name: aws
  runtime: python3.9
  region: ${opt:region, 'us-east-1'}
  stage: ${opt:stage, 'dev'}
  memorySize: 512
  timeout: 30
  
  environment:
    STAGE: ${self:provider.stage}
    AURORA_CLUSTER_ARN: ${env:AURORA_CLUSTER_ARN}
    AURORA_SECRET_ARN: ${env:AURORA_SECRET_ARN}
    DYNAMODB_CACHE_TABLE: ${self:service}-${self:provider.stage}-cache
    SQS_QUEUE_URL: !Ref ScanQueue
  
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - rds-data:ExecuteStatement
            - rds-data:BatchExecuteStatement
          Resource: ${env:AURORA_CLUSTER_ARN}
        - Effect: Allow
          Action:
            - secretsmanager:GetSecretValue
          Resource: ${env:AURORA_SECRET_ARN}
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:UpdateItem
            - dynamodb:DeleteItem
            - dynamodb:Query
            - dynamodb:Scan
          Resource: !GetAtt CacheTable.Arn
        - Effect: Allow
          Action:
            - sqs:SendMessage
            - sqs:ReceiveMessage
            - sqs:DeleteMessage
            - sqs:GetQueueAttributes
          Resource: !GetAtt ScanQueue.Arn
        - Effect: Allow
          Action:
            - s3:GetObject
            - s3:ListBucket
            - s3:GetBucketPolicy
            - s3:GetBucketVersioning
            - s3:GetBucketTagging
            - s3:GetEncryptionConfiguration
            - s3:GetLifecycleConfiguration
          Resource: '*'
        - Effect: Allow
          Action:
            - sagemaker:DescribeNotebookInstance
            - sagemaker:DescribeEndpoint
            - sagemaker:DescribeModel
            - sagemaker:ListNotebookInstances
            - sagemaker:ListEndpoints
            - sagemaker:ListModels
          Resource: '*'
        - Effect: Allow
          Action:
            - iam:GetRole
            - iam:GetRolePolicy
            - iam:ListRoles
            - iam:ListRolePolicies
            - iam:ListAttachedRolePolicies
          Resource: '*'

functions:
  api:
    handler: lambda/api/handler.lambda_handler
    events:
      - httpApi:
          path: /{proxy+}
          method: ANY
    layers:
      - !Ref PythonRequirementsLambdaLayer
  
  scanner:
    handler: lambda/workers/scanner.lambda_handler
    timeout: 900
    memorySize: 1024
    events:
      - sqs:
          arn: !GetAtt ScanQueue.Arn
          batchSize: 1
    layers:
      - !Ref PythonRequirementsLambdaLayer
  
  scheduledScan:
    handler: lambda/workers/scheduled.lambda_handler
    timeout: 900
    memorySize: 1024
    events:
      - schedule:
          rate: cron(0 2 * * ? *)
          description: 'Daily governance scan at 2 AM UTC'
    layers:
      - !Ref PythonRequirementsLambdaLayer

layers:
  pythonRequirements:
    path: lambda/layers
    compatibleRuntimes:
      - python3.9

resources:
  Resources:
    CacheTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:service}-${self:provider.stage}-cache
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: key
            AttributeType: S
        KeySchema:
          - AttributeName: key
            KeyType: HASH
        TimeToLiveSpecification:
          Enabled: true
          AttributeName: ttl
    
    ScanQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:service}-${self:provider.stage}-scan-queue
        VisibilityTimeout: 900
        MessageRetentionPeriod: 86400
    
    ResultsBucket:
      Type: AWS::S3::Bucket
      Properties:
        BucketName: ${self:service}-${self:provider.stage}-results
        VersioningConfiguration:
          Status: Enabled
        PublicAccessBlockConfiguration:
          BlockPublicAcls: true
          BlockPublicPolicy: true
          IgnorePublicAcls: true
          RestrictPublicBuckets: true

  Outputs:
    ApiUrl:
      Description: API Gateway endpoint URL
      Value: !Sub https://${HttpApi}.execute-api.${AWS::Region}.amazonaws.com
    
    ScanQueueUrl:
      Description: SQS Queue URL for scan jobs
      Value: !Ref ScanQueue
    
    CacheTableName:
      Description: DynamoDB cache table name
      Value: !Ref CacheTable
    
    ResultsBucketName:
      Description: S3 bucket for scan results
      Value: !Ref ResultsBucket

plugins:
  - serverless-python-requirements
  - serverless-offline

custom:
  pythonRequirements:
    dockerizePip: true
    layer: true
EOF
print_status "serverless.yml created"

# Step 4: Create Lambda API handler
print_info "Creating Lambda API handler..."
cat > lambda/api/handler.py << 'EOF'
"""
Lambda handler for API Gateway
Wraps the FastAPI application using Mangum
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../webapp/backend'))

from mangum import Mangum
from app.main import app

# Wrap FastAPI with Mangum for Lambda
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    return handler(event, context)
EOF
print_status "Lambda API handler created"

# Step 5: Create Lambda scanner worker
print_info "Creating Lambda scanner worker..."
cat > lambda/workers/scanner.py << 'EOF'
"""
Lambda handler for processing scan jobs from SQS
"""
import sys
import os
import json
import boto3
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from scanners.s3_scanner import S3Scanner
from scanners.sagemaker_scanner import SageMakerScanner
from scanners.iam_scanner import IAMScanner

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """Process scan jobs from SQS"""
    
    results = []
    
    for record in event['Records']:
        try:
            # Parse message
            message = json.loads(record['body'])
            scan_type = message.get('scan_type', 's3')
            region = message.get('region', 'us-east-1')
            
            print(f"Processing {scan_type} scan for region {region}")
            
            # Run appropriate scanner
            if scan_type == 's3':
                scanner = S3Scanner(region=region)
                scan_results = scanner.scan_all_buckets()
            elif scan_type == 'sagemaker':
                scanner = SageMakerScanner(region=region)
                scan_results = scanner.scan()
            elif scan_type == 'iam':
                scanner = IAMScanner(region=region)
                scan_results = scanner.scan()
            else:
                raise ValueError(f"Unknown scan type: {scan_type}")
            
            # Store results in S3
            bucket_name = os.environ.get('RESULTS_BUCKET')
            timestamp = datetime.now().isoformat()
            key = f"scans/{scan_type}/{timestamp}.json"
            
            s3.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=json.dumps(scan_results, indent=2),
                ContentType='application/json'
            )
            
            results.append({
                'scan_type': scan_type,
                'status': 'success',
                'results_location': f"s3://{bucket_name}/{key}",
                'findings_count': len(scan_results.get('findings', []))
            })
            
            print(f"Scan complete: {len(scan_results.get('findings', []))} findings")
            
        except Exception as e:
            print(f"Error processing scan: {str(e)}")
            results.append({
                'scan_type': message.get('scan_type', 'unknown'),
                'status': 'error',
                'error': str(e)
            })
    
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
EOF
print_status "Lambda scanner worker created"

# Step 6: Create scheduled scan handler
print_info "Creating scheduled scan handler..."
cat > lambda/workers/scheduled.py << 'EOF'
"""
Lambda handler for scheduled scans
Triggered by EventBridge on a schedule
"""
import json
import boto3
from datetime import datetime

sqs = boto3.client('sqs')

def lambda_handler(event, context):
    """Trigger daily governance scans"""
    
    queue_url = os.environ.get('SQS_QUEUE_URL')
    
    # Queue scan jobs
    scan_types = ['s3', 'sagemaker', 'iam']
    regions = ['us-east-1']  # Add more regions as needed
    
    for scan_type in scan_types:
        for region in regions:
            message = {
                'scan_type': scan_type,
                'region': region,
                'scheduled': True,
                'timestamp': datetime.now().isoformat()
            }
            
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message)
            )
            
            print(f"Queued {scan_type} scan for {region}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Scans queued successfully',
            'scans_queued': len(scan_types) * len(regions)
        })
    }
EOF
print_status "Scheduled scan handler created"

# Step 7: Create Lambda requirements.txt
print_info "Creating Lambda requirements.txt..."
cat > lambda/requirements.txt << 'EOF'
# Lambda-specific dependencies
mangum==0.17.0
boto3==1.34.0
botocore==1.34.0

# FastAPI and dependencies
fastapi==0.104.1
pydantic==2.5.0
uvicorn==0.24.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9

# Scanners
pandas==2.0.0
numpy==1.24.0
pyyaml==6.0

# Utilities
python-dateutil==2.8.2
jinja2==3.1.2
EOF
print_status "Lambda requirements.txt created"

# Step 8: Update README
print_info "Updating README for serverless..."
cat > README_SERVERLESS.md << 'EOF'
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
EOF
print_status "README_SERVERLESS.md created"

# Step 9: Create package.json for Serverless plugins
print_info "Creating package.json..."
cat > package.json << 'EOF'
{
  "name": "grc-ai-governance-serverless",
  "version": "1.0.0",
  "description": "AWS AI Governance Framework - Serverless Edition",
  "main": "index.js",
  "scripts": {
    "deploy": "serverless deploy",
    "deploy:prod": "serverless deploy --stage prod",
    "remove": "serverless remove",
    "logs": "serverless logs -f api --tail"
  },
  "devDependencies": {
    "serverless": "^3.38.0",
    "serverless-python-requirements": "^6.1.0",
    "serverless-offline": "^13.3.0"
  }
}
EOF
print_status "package.json created"

# Step 10: Create .gitignore updates
print_info "Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Serverless
.serverless/
node_modules/
.build/
lambda/layers/

# Lambda
*.zip
lambda-package/
EOF
print_status ".gitignore updated"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Migration Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Install Node.js dependencies: npm install"
echo "2. Set environment variables for Aurora and Secrets Manager"
echo "3. Deploy: serverless deploy --stage dev"
echo "4. Test: curl \$API_URL/health"
echo ""
echo "See README_SERVERLESS.md for full deployment guide"
echo ""
