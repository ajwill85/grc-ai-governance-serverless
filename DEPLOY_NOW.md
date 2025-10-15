# 🚀 Deploy Now - Quick Start Guide

**Ready to deploy your serverless GRC AI Governance Framework!**

---

## Option 1: Automated Deployment (Recommended)

### Step 1: Deploy to GitHub
```bash
./scripts/deployment/setup_github.sh
```
This script will:
- Initialize git repository
- Create initial commit
- Guide you through GitHub setup
- Push to your new repository

### Step 2: Deploy to AWS
```bash
./scripts/deployment/deploy_to_aws.sh
```
This script will:
- Check prerequisites
- Create Aurora Serverless database (if needed)
- Deploy Lambda functions
- Set up API Gateway
- Provide your API endpoints

---

## Option 2: Manual Deployment

### GitHub Setup
```bash
# 1. Initialize git
git init

# 2. Add all files
git add .

# 3. Create commit
git commit -m "Initial commit: GRC AI Governance Framework - Serverless Edition"

# 4. Create repository on GitHub.com
# Go to: https://github.com/new
# Name: grc-ai-governance-serverless
# Keep it PUBLIC, don't initialize with README

# 5. Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/grc-ai-governance-serverless.git
git branch -M main
git push -u origin main
```

### AWS Deployment
```bash
# 1. Configure AWS CLI
aws configure

# 2. Create Aurora Serverless (optional - script will do this)
# See DEPLOYMENT_READY.md for manual steps

# 3. Set environment variables
export AURORA_CLUSTER_ARN="arn:aws:rds:..."
export AURORA_SECRET_ARN="arn:aws:secretsmanager:..."

# 4. Deploy
serverless deploy --stage prod --region us-east-1
```

---

## 📋 Pre-Deployment Checklist

✅ **Required:**
- [ ] AWS Account
- [ ] GitHub Account
- [ ] Node.js installed
- [ ] AWS CLI configured (`aws configure`)

✅ **Automatic (scripts handle this):**
- [ ] Serverless Framework
- [ ] Aurora Serverless database
- [ ] Secrets Manager setup
- [ ] Git repository

---

## 🎯 What You'll Get

### On GitHub
- Public repository with your serverless framework
- Professional README and documentation
- Clean commit history
- Ready for collaboration

### On AWS
- **API Endpoint**: `https://xxx.execute-api.us-east-1.amazonaws.com`
- **Lambda Functions**: 3 functions deployed
- **Aurora Database**: Serverless v2 with auto-pause
- **DynamoDB**: Cache table
- **API Gateway**: REST API
- **CloudWatch**: Logs and monitoring

### Costs
- **Monthly**: ~$55
- **Free Tier**: May be less if eligible
- **Pay-per-use**: Only charged for actual usage

---

## 🚦 Quick Deploy Commands

```bash
# Complete deployment in 2 commands:
./scripts/deployment/setup_github.sh
./scripts/deployment/deploy_to_aws.sh
```

---

## 📊 Post-Deployment

### Test Your API
```bash
# Your API URL will be shown after deployment
API_URL="https://your-api.execute-api.us-east-1.amazonaws.com"

# Test health
curl $API_URL/health

# View docs
open $API_URL/docs
```

### Monitor
```bash
# View logs
serverless logs -f api --tail --stage prod

# View metrics
serverless metrics --stage prod
```

### Update
```bash
# Push changes to GitHub
git add .
git commit -m "Update: your changes"
git push

# Deploy updates to AWS
serverless deploy --stage prod
```

---

## 🆘 Troubleshooting

### GitHub Issues
- **Authentication failed**: Create a personal access token
- **Repository exists**: Use a different name or delete existing

### AWS Issues
- **Credentials not configured**: Run `aws configure`
- **Insufficient permissions**: Ensure IAM user has necessary permissions
- **Region issues**: Use `us-east-1` for best compatibility

### Common Fixes
```bash
# Install Serverless Framework
npm install -g serverless

# Check AWS credentials
aws sts get-caller-identity

# Check Node version (should be 14+)
node --version
```

---

## 📚 Documentation

- **Full Deployment Guide**: `DEPLOYMENT_READY.md`
- **Project Structure**: `PROJECT_STRUCTURE.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **Cost Analysis**: `context_files/security_analysis/COST_ANALYSIS.md`

---

## ✨ Ready to Deploy!

Your project is:
- ✅ Organized and clean
- ✅ Documentation complete
- ✅ Scripts ready
- ✅ No sensitive data
- ✅ Production ready

**Deploy with confidence!** 🚀

---

**Deployment Time**: ~30 minutes  
**Monthly Cost**: ~$55  
**Support**: Check the documentation in `context_files/`

**Let's deploy your serverless GRC framework!** 🎉
