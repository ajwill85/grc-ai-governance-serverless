#!/bin/bash

# Local Development Server Startup Script
# Sets dummy environment variables for serverless offline

echo "🚀 Starting Local Serverless Development Server..."
echo "----------------------------------------"

# Export dummy environment variables for local testing
export AURORA_CLUSTER_ARN="arn:aws:rds:us-east-1:123456789012:cluster:local-test"
export AURORA_SECRET_ARN="arn:aws:secretsmanager:us-east-1:123456789012:secret:local-test"
export DATABASE_URL="sqlite:///./test.db"
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="local-test-key"
export AWS_SECRET_ACCESS_KEY="local-test-secret"

echo "✅ Environment variables set for local testing"
echo ""
echo "📍 Starting server on http://localhost:3000"
echo "📚 API Documentation: http://localhost:3000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "----------------------------------------"
echo ""

# Start serverless offline
npx serverless offline start --stage local --noAuth
