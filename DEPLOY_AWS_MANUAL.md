# Manual AWS Deployment Guide

**Region**: us-east-1

---

## Important: Aurora Serverless Setup Required

Before deploying the Lambda functions, you need to set up Aurora Serverless v2 database.

### Option 1: Skip Database (Deploy Lambda Only)

If you want to deploy just the Lambda functions without the database first:

```bash
# Deploy without database (will fail on first API call but Lambda will be deployed)
npm run deploy
```

### Option 2: Create Aurora Serverless First (Recommended)

This will take 10-15 minutes but is required for the app to work.

---

## Step-by-Step Deployment

### Step 1: Create Aurora Serverless v2 Database

```bash
# Generate a secure password
DB_PASSWORD=$(openssl rand -base64 32)
echo "Database Password: $DB_PASSWORD"
echo "SAVE THIS PASSWORD!"

# Get your VPC and subnet information
aws ec2 describe-vpcs --region us-east-1
aws ec2 describe-subnets --region us-east-1

# You'll need:
# - VPC ID (vpc-xxx)
# - At least 2 subnet IDs in different AZs
# - Security group ID (or create one)
```

#### Create DB Subnet Group
```bash
# Replace with your subnet IDs
aws rds create-db-subnet-group \
  --db-subnet-group-name grc-db-subnet-group \
  --db-subnet-group-description "GRC Serverless DB Subnet Group" \
  --subnet-ids subnet-YOUR_SUBNET_1 subnet-YOUR_SUBNET_2 \
  --region us-east-1
```

#### Create Security Group (if needed)
```bash
# Get your VPC ID first
VPC_ID=$(aws ec2 describe-vpcs --query 'Vpcs[0].VpcId' --output text --region us-east-1)

# Create security group
aws ec2 create-security-group \
  --group-name grc-db-sg \
  --description "Security group for GRC database" \
  --vpc-id $VPC_ID \
  --region us-east-1

# Get the security group ID
SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=grc-db-sg" \
  --query 'SecurityGroups[0].GroupId' \
  --output text \
  --region us-east-1)

# Allow PostgreSQL access from within VPC
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 5432 \
  --cidr 10.0.0.0/8 \
  --region us-east-1
```

#### Create Aurora Cluster
```bash
# Create Aurora Serverless v2 cluster
aws rds create-db-cluster \
  --db-cluster-identifier grc-aurora-dev \
  --engine aurora-postgresql \
  --engine-version 15.4 \
  --master-username grc_admin \
  --master-user-password "$DB_PASSWORD" \
  --database-name grc_governance \
  --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=2 \
  --enable-http-endpoint \
  --db-subnet-group-name grc-db-subnet-group \
  --vpc-security-group-ids $SG_ID \
  --region us-east-1

# Create Aurora instance
aws rds create-db-instance \
  --db-instance-identifier grc-aurora-dev-instance \
  --db-instance-class db.serverless \
  --engine aurora-postgresql \
  --db-cluster-identifier grc-aurora-dev \
  --region us-east-1

# Wait for cluster (10-15 minutes)
echo "Waiting for Aurora cluster to be available..."
aws rds wait db-cluster-available \
  --db-cluster-identifier grc-aurora-dev \
  --region us-east-1

echo "Aurora cluster is ready!"
```

### Step 2: Store Database Credentials

```bash
# Get cluster endpoint
CLUSTER_ENDPOINT=$(aws rds describe-db-clusters \
  --db-cluster-identifier grc-aurora-dev \
  --query 'DBClusters[0].Endpoint' \
  --output text \
  --region us-east-1)

# Create secret in Secrets Manager
aws secretsmanager create-secret \
  --name grc/database-dev \
  --description "GRC Database Credentials (dev)" \
  --secret-string "{
    \"username\": \"grc_admin\",
    \"password\": \"$DB_PASSWORD\",
    \"engine\": \"postgres\",
    \"host\": \"$CLUSTER_ENDPOINT\",
    \"port\": 5432,
    \"dbname\": \"grc_governance\"
  }" \
  --region us-east-1
```

### Step 3: Get ARNs for Deployment

```bash
# Get Aurora cluster ARN
export AURORA_CLUSTER_ARN=$(aws rds describe-db-clusters \
  --db-cluster-identifier grc-aurora-dev \
  --query 'DBClusters[0].DBClusterArn' \
  --output text \
  --region us-east-1)

# Get secret ARN
export AURORA_SECRET_ARN=$(aws secretsmanager describe-secret \
  --secret-id grc/database-dev \
  --query 'ARN' \
  --output text \
  --region us-east-1)

# Display ARNs
echo "AURORA_CLUSTER_ARN=$AURORA_CLUSTER_ARN"
echo "AURORA_SECRET_ARN=$AURORA_SECRET_ARN"

# Save these for deployment!
```

### Step 4: Deploy Serverless Application

```bash
# Set environment variables
export AURORA_CLUSTER_ARN="<your-cluster-arn>"
export AURORA_SECRET_ARN="<your-secret-arn>"

# Deploy to development
npm run deploy

# Or deploy to production
npm run deploy:prod
```

---

## Quick Deploy (If Database Already Exists)

If you already have Aurora Serverless set up:

```bash
# Set ARNs (replace with your actual ARNs)
export AURORA_CLUSTER_ARN="arn:aws:rds:us-east-1:YOUR_ACCOUNT_ID:cluster:grc-aurora-dev"
export AURORA_SECRET_ARN="arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:grc/database-dev-xxxxx"

# Deploy to development
npm run deploy

# Deploy to production
npm run deploy:prod
```

---

## Test Deployment

```bash
# Get API endpoint from serverless info
serverless info --stage dev

# Test health endpoint
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/health

# View API docs
open https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/docs

# Initialize database
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/api/v1/admin/init-db
```

---

## View Deployment Info

```bash
# View all deployment info
serverless info --stage dev

# View logs (using npm script)
npm run logs

# Or view logs directly
serverless logs -f api --tail --stage dev
```

---

## Remove Deployment

```bash
# Remove all Lambda functions and resources
npm run remove

# Or remove specific stage
serverless remove --stage dev

# Delete Aurora cluster (if needed)
aws rds delete-db-instance \
  --db-instance-identifier grc-aurora-dev-instance \
  --skip-final-snapshot \
  --region us-east-1

aws rds delete-db-cluster \
  --db-cluster-identifier grc-aurora-dev \
  --skip-final-snapshot \
  --region us-east-1

# Delete secret
aws secretsmanager delete-secret \
  --secret-id grc/database-dev \
  --force-delete-without-recovery \
  --region us-east-1
```

---

## Cost Estimate

- **Aurora Serverless v2**: $15-30/month (with auto-pause)
- **Lambda**: $5-10/month
- **API Gateway**: $3.50/month
- **DynamoDB**: $3/month
- **Other**: $10-20/month
- **Total**: ~$40-70/month

---

## Troubleshooting

### Issue: VPC/Subnet not found
- Use default VPC or create one
- Ensure subnets are in different AZs

### Issue: Permission denied
- Ensure IAM user has necessary permissions
- Check: RDS, Secrets Manager, Lambda, API Gateway, DynamoDB

### Issue: Deployment fails
- Check CloudFormation console for detailed errors
- View logs: `npm run logs` or `serverless logs -f api --stage dev`
- Verify environment variables are set: `echo $AURORA_CLUSTER_ARN`

### Issue: Python version mismatch
- Ensure Python 3.11 is installed: `python3.11 --version`
- Update serverless.yml runtime if needed
- Rebuild dependencies: `rm -rf node_modules && npm install`

---

## Prerequisites

Before deploying, ensure you have:

- **Python 3.11+** installed and configured
- **Node.js and npm** for serverless framework
- **AWS CLI** configured with appropriate credentials
- **IAM permissions** for RDS, Lambda, API Gateway, DynamoDB, Secrets Manager

```bash
# Verify prerequisites
python3.11 --version
node --version
npm --version
aws --version
aws sts get-caller-identity
```

## Environment Setup

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Verify serverless installation
serverless --version
```

**Ready to deploy!** Start with Step 1 to create the Aurora database.
