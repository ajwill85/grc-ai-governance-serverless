#!/bin/bash

# GitHub Setup Script for GRC AI Governance Serverless
# This script prepares and pushes the project to a new GitHub repository

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}GitHub Setup Script${NC}"
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

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi
print_status "Git found"

# Check if already a git repository
if [ -d .git ]; then
    print_info "Git repository already initialized"
    
    # Check for existing remote
    if git remote get-url origin &> /dev/null; then
        EXISTING_REMOTE=$(git remote get-url origin)
        print_warning "Existing remote found: $EXISTING_REMOTE"
        echo ""
        echo "Do you want to:"
        echo "1. Keep existing remote and push updates"
        echo "2. Remove existing remote and set up new one"
        echo "3. Exit without changes"
        read -p "Choose (1/2/3): " CHOICE
        
        case $CHOICE in
            1)
                print_info "Keeping existing remote"
                ;;
            2)
                print_info "Removing existing remote"
                git remote remove origin
                ;;
            3)
                print_info "Exiting without changes"
                exit 0
                ;;
            *)
                print_error "Invalid choice"
                exit 1
                ;;
        esac
    fi
else
    print_info "Initializing git repository"
    git init
    print_status "Git repository initialized"
fi

# Check git status
print_info "Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    print_info "Uncommitted changes found"
    
    # Add all files
    print_info "Adding files to git..."
    git add .
    print_status "Files added"
    
    # Create commit
    print_info "Creating commit..."
    git commit -m "feat: GRC AI Governance Framework - Serverless Edition

- Serverless architecture with AWS Lambda
- Aurora Serverless v2 for database
- DynamoDB for caching
- API Gateway for REST endpoints
- 60% cost savings vs ECS architecture
- AWS resource scanners (S3, IAM, SageMaker)
- OPA policy engine with 35+ rules
- ISO 27001/27701/42001 compliance mapping
- FastAPI backend + React frontend
- Comprehensive documentation
- Production-ready deployment scripts" || print_warning "Nothing to commit"
    
    print_status "Commit created"
else
    print_info "No changes to commit"
fi

# Get GitHub username
echo ""
read -p "Enter your GitHub username: " GITHUB_USERNAME
if [ -z "$GITHUB_USERNAME" ]; then
    print_error "GitHub username is required"
    exit 1
fi

# Get repository name
read -p "Enter repository name [grc-ai-governance-serverless]: " REPO_NAME
REPO_NAME=${REPO_NAME:-grc-ai-governance-serverless}

# Check if remote already exists
if ! git remote get-url origin &> /dev/null; then
    # Add remote
    print_info "Adding GitHub remote..."
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    print_status "Remote added"
fi

# Set main branch
print_info "Setting main branch..."
git branch -M main
print_status "Main branch set"

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}IMPORTANT: GitHub Repository Setup${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "Before pushing, you need to create the repository on GitHub:"
echo ""
echo "1. Go to: https://github.com/new"
echo "2. Repository name: $REPO_NAME"
echo "3. Description: AWS AI Governance Framework - Serverless Edition with Lambda, Aurora Serverless v2, and 60% cost savings"
echo "4. Set as: Public"
echo "5. DO NOT initialize with README"
echo "6. DO NOT add .gitignore"
echo "7. DO NOT add license"
echo "8. Click 'Create repository'"
echo ""
read -p "Press Enter when you've created the repository..."

# Push to GitHub
print_info "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}GitHub Setup Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "Recommended GitHub topics to add:"
    echo "  - aws"
    echo "  - serverless"
    echo "  - lambda"
    echo "  - governance"
    echo "  - compliance"
    echo "  - iso27001"
    echo "  - ai-governance"
    echo "  - fastapi"
    echo "  - react"
    echo "  - typescript"
    echo "  - opa"
    echo "  - policy-as-code"
    echo ""
    echo "Next steps:"
    echo "1. Add topics on GitHub"
    echo "2. Add a description"
    echo "3. Deploy to AWS: ./scripts/deployment/deploy_to_aws.sh"
    echo "4. Share your project!"
else
    print_error "Push failed. Please check your GitHub credentials and repository settings."
    echo ""
    echo "If you're using 2FA, you may need to:"
    echo "1. Create a personal access token: https://github.com/settings/tokens"
    echo "2. Use the token as your password when pushing"
    echo ""
    echo "Or use SSH instead:"
    echo "git remote set-url origin git@github.com:$GITHUB_USERNAME/$REPO_NAME.git"
fi

print_status "Script complete!"
