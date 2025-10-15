#!/bin/bash

# AWS Deployment Script for GRC AI Governance Serverless
# This script deploys the application to AWS

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AWS Deployment Script${NC}"
echo -e "${BLUE}GRC AI Governance - Serverless Edition${NC}"
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

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
print_info "Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI not found. Please install it first."
    echo "Visit: https://aws.amazon.com/cli/"
    exit 1
fi
print_status "AWS CLI found"

# Check Serverless Framework
if ! command -v serverless &> /dev/null; then
    print_error "Serverless Framework not found. Installing..."
    npm install -g serverless
fi
print_status "Serverless Framework found"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured."
    echo "Run: aws configure"
    exit 1
fi
print_status "AWS credentials configured"

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
print_info "AWS Account: $ACCOUNT_ID"

# Get deployment stage
echo ""
read -p "Enter deployment stage (dev/prod) [dev]: " STAGE
STAGE=${STAGE:-dev}
print_info "Deployment stage: $STAGE"

# Get AWS region
read -p "Enter AWS region [us-east-1]: " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}
print_info "AWS region: $AWS_REGION"

# Check for Aurora cluster
echo ""
print_info "Checking for Aurora Serverless cluster..."
if aws rds describe-db-clusters --db-cluster-identifier grc-aurora-serverless-$STAGE &> /dev/null; then
    print_status "Aurora cluster exists"
    
    # Get cluster ARN
    export AURORA_CLUSTER_ARN=$(aws rds describe-db-clusters \
        --db-cluster-identifier grc-aurora-serverless-$STAGE \
        --query 'DBClusters[0].DBClusterArn' \
        --output text \
        --region $AWS_REGION)
    
    # Get secret ARN
    export AURORA_SECRET_ARN=$(aws secretsmanager describe-secret \
        --secret-id grc/database-$STAGE \
        --query 'ARN' \
        --output text \
        --region $AWS_REGION 2>/dev/null || echo "")
    
    if [ -z "$AURORA_SECRET_ARN" ]; then
        print_warning "Secret not found. You may need to create it."
    fi
else
    print_warning "Aurora cluster not found."
    echo ""
    echo "Would you like to create it now? (y/n)"
    read -p "> " CREATE_DB
    
    if [ "$CREATE_DB" = "y" ]; then
        print_info "Creating Aurora Serverless v2 cluster..."
        
        # Generate password
        DB_PASSWORD=$(openssl rand -base64 32)
        
        # Create cluster
        aws rds create-db-cluster \
            --db-cluster-identifier grc-aurora-serverless-$STAGE \
            --engine aurora-postgresql \
            --engine-version 15.4 \
            --master-username grc_admin \
            --master-user-password "$DB_PASSWORD" \
            --database-name grc_governance \
            --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=2 \
            --enable-http-endpoint \
            --region $AWS_REGION
        
        # Create instance
        aws rds create-db-instance \
            --db-instance-identifier grc-aurora-serverless-$STAGE-instance \
            --db-instance-class db.serverless \
            --engine aurora-postgresql \
            --db-cluster-identifier grc-aurora-serverless-$STAGE \
            --region $AWS_REGION
        
        print_info "Waiting for cluster to be available (this may take 5-10 minutes)..."
        aws rds wait db-cluster-available \
            --db-cluster-identifier grc-aurora-serverless-$STAGE \
            --region $AWS_REGION
        
        print_status "Aurora cluster created"
        
        # Store secret
        CLUSTER_ENDPOINT=$(aws rds describe-db-clusters \
            --db-cluster-identifier grc-aurora-serverless-$STAGE \
            --query 'DBClusters[0].Endpoint' \
            --output text)
        
        aws secretsmanager create-secret \
            --name grc/database-$STAGE \
            --description "GRC Database Credentials ($STAGE)" \
            --secret-string "{
                \"username\": \"grc_admin\",
                \"password\": \"$DB_PASSWORD\",
                \"engine\": \"postgres\",
                \"host\": \"$CLUSTER_ENDPOINT\",
                \"port\": 5432,
                \"dbname\": \"grc_governance\"
            }" \
            --region $AWS_REGION
        
        print_status "Database credentials stored in Secrets Manager"
        echo ""
        echo -e "${YELLOW}IMPORTANT: Save this password securely!${NC}"
        echo "Database Password: $DB_PASSWORD"
        echo ""
        
        # Get ARNs
        export AURORA_CLUSTER_ARN=$(aws rds describe-db-clusters \
            --db-cluster-identifier grc-aurora-serverless-$STAGE \
            --query 'DBClusters[0].DBClusterArn' \
            --output text)
        
        export AURORA_SECRET_ARN=$(aws secretsmanager describe-secret \
            --secret-id grc/database-$STAGE \
            --query 'ARN' \
            --output text)
    else
        print_error "Aurora cluster is required for deployment."
        exit 1
    fi
fi

# Display ARNs
echo ""
print_info "Configuration:"
echo "  AURORA_CLUSTER_ARN: $AURORA_CLUSTER_ARN"
echo "  AURORA_SECRET_ARN: $AURORA_SECRET_ARN"

# Deploy application
echo ""
print_info "Deploying serverless application..."
serverless deploy --stage $STAGE --region $AWS_REGION --verbose

# Get API endpoint
API_URL=$(serverless info --stage $STAGE --region $AWS_REGION --verbose | grep "ANY" | grep -oE "https://[^ ]+")

if [ ! -z "$API_URL" ]; then
    # Remove {proxy+} from URL
    API_URL=${API_URL%/{proxy+}}
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment Successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "API Endpoint: $API_URL"
    echo "API Documentation: $API_URL/docs"
    echo "Health Check: $API_URL/health"
    echo ""
    
    # Test health endpoint
    print_info "Testing health endpoint..."
    curl -s $API_URL/health | python3 -m json.tool || print_warning "Health check failed"
    
    echo ""
    echo "Next steps:"
    echo "1. Initialize database: curl -X POST $API_URL/api/v1/admin/init-db"
    echo "2. View API docs: $API_URL/docs"
    echo "3. Monitor logs: serverless logs -f api --tail --stage $STAGE"
else
    print_warning "Could not retrieve API endpoint. Check deployment status:"
    echo "serverless info --stage $STAGE --region $AWS_REGION"
fi

echo ""
print_status "Deployment complete!"
