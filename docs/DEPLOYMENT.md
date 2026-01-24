# Production Deployment Guide

## Prerequisites
- AWS CLI configured with credentials
- Terraform installed
- All dev infrastructure working properly

## Phase 1: Deploy Production Infrastructure (Run Manually First)

### Step 1: Create S3 Buckets (Prod)
```bash
cd d:\AI-Project\transinia\backend\infra\s3-bucket-infra
terraform init
terraform apply -var-file="prod.tfvars"
```

**Expected Output:**
- S3 Bucket: `transinia-prod-transcripts`
- S3 Bucket: `transinia-prod-outputs`

---

### Step 2: Create DynamoDB Tables (Prod)
```bash
cd d:\AI-Project\transinia\backend\infra\dynamodb-infra
terraform init
terraform apply -var-file="prod.tfvars"
```

**Expected Output:**
- DynamoDB Table: `transinia-prod-meetings`
- DynamoDB Table: `transinia-prod-actions`

---

### Step 3: Create ECS Infrastructure (Prod)
```bash
cd d:\AI-Project\transinia\backend\infra\ecs-fargate-infra
terraform init
terraform apply -var-file="prod.tfvars"
```

**Expected Output:**
- VPC with public/private subnets
- Application Load Balancer (ALB)
- ECS Fargate Cluster: `transinia-prod-cluster`
- ECS Services (backend/frontend)
- ECR Repositories
- IAM Roles

**IMPORTANT:** Copy the ALB DNS output:
```bash
terraform output -raw alb_dns_name
```
Example output: `transinia-prod-alb-XXXXXXXXXX.us-east-1.elb.amazonaws.com`

---

## Phase 2: Configure GitHub Secrets

Go to: https://github.com/HarsimranKaur06/Transinia/settings/secrets/actions

Add these production secrets:

| Secret Name | Value | Example |
|------------|-------|---------|
| `PROD_ALB_DNS_NAME` | ALB DNS from Step 3 | `transinia-prod-alb-XXXXX.us-east-1.elb.amazonaws.com` |
| `PROD_S3_BUCKET_RAW` | S3 raw bucket name | `transinia-prod-transcripts` |
| `PROD_S3_BUCKET_PROCESSED` | S3 processed bucket name | `transinia-prod-outputs` |
| `PROD_DYNAMODB_TABLE_MEETINGS` | DynamoDB meetings table | `transinia-prod-meetings` |
| `PROD_DYNAMODB_TABLE_ACTIONS` | DynamoDB actions table | `transinia-prod-actions` |
| `PROD_SENTRY_DSN` | Sentry DSN for prod monitoring | See Sentry Setup below |
| `DEV_SENTRY_DSN` | Sentry DSN for dev monitoring | See Sentry Setup below |

**Note:** These secrets use the same AWS credentials as dev:
- `AWS_ACCOUNT_ID` (already set)
- `AWS_REGION` (already set)
- `AWS_ACCESS_KEY_ID` (already set)
- `AWS_SECRET_ACCESS_KEY` (already set)
- `OPENAI_API_KEY` (already set)

---

## Phase 2.5: Configure Sentry Monitoring (Optional but Recommended)

### Why Sentry?
- Real-time error tracking and alerting
- Performance monitoring (APM)
- Stack traces with code context
- Automatic sensitive data filtering (AWS keys, API keys)

### Setup Steps:

1. **Sign up for Sentry** (if not already):
   - Go to: https://sentry.io/signup/
   - Free tier: 5,000 errors/month

2. **Create Dev Project:**
   - Platform: **FastAPI**
   - Project name: `transinia-dev`
   - Copy the DSN (format: `https://xxxxx@xxx.ingest.sentry.io/xxxxx`)
   - Add to GitHub Secrets as `DEV_SENTRY_DSN`

3. **Create Prod Project:**
   - Platform: **FastAPI**
   - Project name: `transinia-prod`
   - Copy the DSN
   - Add to GitHub Secrets as `PROD_SENTRY_DSN`

4. **Verify Setup:**
   - After deployment, check logs:
     ```bash
     aws logs tail /ecs/transinia-prod-backend --since 5m --region us-east-1 | Select-String "Sentry"
     ```
   - Should see: `"Sentry initialized with sensitive data filtering"`

5. **Access Sentry Dashboard:**
   - Issues: https://sentry.io/issues/
   - Performance: https://sentry.io/performance/
   - Dashboards: https://sentry.io/dashboards/

**Security Note:** Sentry integration includes automatic filtering of:
- AWS Access Keys
- AWS Secret Keys
- OpenAI API Keys
- Authorization headers
- Environment variables

---

## Phase 3: Sync Code (Dev → Master → Deploy)

### Option A: Merge via GitHub UI (Recommended)
1. Go to: https://github.com/HarsimranKaur06/Transinia
2. Click "Pull requests" → "New pull request"
3. Base: `master` ← Compare: `dev`
4. Create and merge the pull request
5. Production deployment will trigger automatically

### Option B: Merge via Command Line
```bash
cd d:\AI-Project\transinia

# Switch to master
git checkout master

# Pull latest changes
git pull origin master

# Merge dev into master
git merge dev

# Push to trigger prod deployment
git push origin master
```

---

## Phase 4: Monitor Deployment

1. **Watch GitHub Actions:**
   - URL: https://github.com/HarsimranKaur06/Transinia/actions
   - Look for "Deploy Infrastructure (prod)" workflow
   - Wait ~10-15 minutes for completion

2. **Verify ECS Services:**
   ```bash
   aws ecs describe-services \
     --cluster transinia-prod-cluster \
     --services transinia-prod-backend-service transinia-prod-frontend-service \
     --query 'services[*].[serviceName,runningCount,desiredCount]' \
     --output table
   ```

3. **Check Application:**
   - Frontend: `http://<PROD_ALB_DNS_NAME>`
   - Backend API: `http://<PROD_ALB_DNS_NAME>/api/health`

---

## Troubleshooting

### Tasks failing health checks?
- Check CloudWatch logs: `/ecs/transinia-prod-backend` and `/ecs/transinia-prod-frontend`
- Verify images were built and pushed to ECR
- Check security groups allow ALB → tasks communication

### CORS errors?
- Verify GitHub Actions ran the "Configure S3 CORS" step
- Check S3 bucket CORS configuration:
  ```bash
  aws s3api get-bucket-cors --bucket transinia-prod-transcripts
  ```

### Need to destroy prod infrastructure?
```bash
# Reverse order: ECS → DynamoDB → S3
cd d:\AI-Project\transinia\backend\infra\ecs-fargate-infra
terraform destroy -var-file="prod.tfvars"

cd ../dynamodb-infra
terraform destroy -var-file="prod.tfvars"

cd ../s3-bucket-infra
terraform destroy -var-file="prod.tfvars"
```

---

## Summary Checklist

- [ ] Step 1: Deploy S3 buckets (prod)
- [ ] Step 2: Deploy DynamoDB tables (prod)
- [ ] Step 3: Deploy ECS infrastructure (prod)
- [ ] Step 4: Copy ALB DNS from terraform output
- [ ] Step 5: Add all 5 production secrets to GitHub
- [ ] Step 6: Merge dev → master (or create PR)
- [ ] Step 7: Watch GitHub Actions deployment
- [ ] Step 8: Verify application is running
- [ ] Step 9: Test frontend and backend endpoints

---

## Quick Command Reference

```bash
# Get ALB DNS
cd backend/infra/ecs-fargate-infra
terraform output -raw alb_dns_name

# Check ECS services
aws ecs list-services --cluster transinia-prod-cluster

# View logs
aws logs tail /ecs/transinia-prod-backend --follow
aws logs tail /ecs/transinia-prod-frontend --follow

# Check deployment status
aws ecs describe-services --cluster transinia-prod-cluster --service transinia-prod-backend-service --region us-east-1

# View task definition history
aws ecs list-task-definitions --family-prefix transinia-prod-backend --region us-east-1

# Rollback to specific revision (if needed)
aws ecs update-service --cluster transinia-prod-cluster --service transinia-prod-backend-service --task-definition transinia-prod-backend:123 --region us-east-1

# Emergency restart only (not recommended for production deploys)
# Use GitHub Actions workflow for proper deployments
aws ecs update-service --cluster transinia-prod-cluster --service transinia-prod-backend-service --force-new-deployment --region us-east-1
```
