# GitHub Setup Instructions

## Option 1: Create Repository via GitHub CLI (Fastest)

If you have GitHub CLI installed:

```bash
# Login to GitHub CLI (if not already)
gh auth login

# Create repository
gh repo create aws-ai-governance-framework \
  --public \
  --description "Multi-tenant SaaS platform for AWS AI/ML compliance monitoring across ISO 27001, 27701, and 42001 standards" \
  --source=. \
  --remote=origin \
  --push
```

## Option 2: Create Repository via Web (Manual)

### Step 1: Create Repository on GitHub.com
1. Go to https://github.com/new
2. Repository name: `aws-ai-governance-framework`
3. Description: `Multi-tenant SaaS platform for AWS AI/ML compliance monitoring across ISO 27001, 27701, and 42001 standards`
4. Choose: **Public** (for portfolio)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### Step 2: Push to GitHub
```bash
cd /Users/ajmm/Library/CloudStorage/ProtonDrive-wraithprivacy@proton.me-folder/Work/repos/grc_ai_privacy

# Add remote
git remote add origin https://github.com/ajwill85/aws-ai-governance-framework.git

# Push to GitHub
git push -u origin main
```

## Option 3: Use SSH (If you have SSH keys set up)

```bash
# Add remote with SSH
git remote add origin git@github.com:ajwill85/aws-ai-governance-framework.git

# Push to GitHub
git push -u origin main
```

---

## After Pushing

### Add Repository Topics (for discoverability)
Go to your repository on GitHub and add these topics:
- `aws`
- `compliance`
- `governance`
- `iso-27001`
- `iso-27701`
- `iso-42001`
- `sagemaker`
- `grc`
- `security`
- `python`
- `fastapi`
- `react`
- `typescript`
- `saas`

### Add Repository Description
Make sure the description is set:
> Multi-tenant SaaS platform for AWS AI/ML compliance monitoring across ISO 27001, 27701, and 42001 standards. Features automated scanning, policy-as-code enforcement, and customizable dashboards.

### Create README Badges (Optional)
Add these to the top of your README.md:

```markdown
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![React](https://img.shields.io/badge/React-18.2+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

---

## Verify Push

After pushing, verify at:
https://github.com/ajwill85/aws-ai-governance-framework

You should see:
- ✅ 41 files
- ✅ All directories (scanners, policies, webapp)
- ✅ README.md displayed
- ✅ Commit message visible

---

## Next: Test the Setup

Once pushed to GitHub, proceed with testing:

```bash
cd webapp
docker-compose up -d
```
