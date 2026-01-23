# Transinia Deployment Guide

## Overview
This guide explains how to deploy the Transinia application to AWS ECS Fargate.

## Prerequisites
- AWS account with appropriate permissions
- Terraform installed locally
- GitHub repository with secrets configured

## Infrastructure Setup (Manual - One-time)

### 1. Deploy S3 Buckets
```bash
cd backend/infra/s3-bucket-infra
terraform init
terraform plan -var-file="terraform.tfvars"  # For dev
# or terraform plan -var-file="prod.tfvars"  # For prod
terraform apply
```

### 2. Deploy DynamoDB Tables
```bash
cd ../dynamodb-infra
terraform init
terraform plan -var-file="terraform.tfvars"  # For dev
terraform apply
```

### 3. Deploy ECS Fargate Infrastructure
```bash
cd ../ecs-fargate-infra
terraform init
terraform plan -var-file="terraform.tfvars"  # For dev
terraform apply
```

### 4. Get Infrastructure Output Values
After Terraform completes, get the required values:
```bash
# Get ALB DNS Name
terraform output alb_dns_name

# Get S3 bucket names (from s3-bucket-infra directory)
terraform output raw_bucket_name
terraform output processed_bucket_name

# Get DynamoDB table names (from dynamodb-infra directory)
terraform output meetings_table_name
terraform output actions_table_name
```

### 5. Configure GitHub Secrets
Add these values to your GitHub repository secrets (Settings → Secrets and variables → Actions):

**For Dev Environment:**
- `DEV_ALB_DNS_NAME` - From ECS Terraform output
- `DEV_S3_BUCKET_RAW` - From S3 Terraform output (e.g., `transinia-dev-transcripts`)
- `DEV_S3_BUCKET_PROCESSED` - From S3 Terraform output (e.g., `transinia-dev-outputs`)
- `DEV_DYNAMODB_TABLE_MEETINGS` - From DynamoDB Terraform output (e.g., `transinia-dev-meetings`)
- `DEV_DYNAMODB_TABLE_ACTIONS` - From DynamoDB Terraform output (e.g., `transinia-dev-actions`)

**For Prod Environment:**
- `PROD_ALB_DNS_NAME`
- `PROD_S3_BUCKET_RAW`
- `PROD_S3_BUCKET_PROCESSED`
- `PROD_DYNAMODB_TABLE_MEETINGS`
- `PROD_DYNAMODB_TABLE_ACTIONS`

## Application Deployment

### Deploy via GitHub Actions
Push to the `dev` branch or manually trigger the workflow:
```bash
git add .
git commit -m "Deploy application"
git push origin dev
```

The workflow will:
1. ✅ Build backend Docker image with tag: `latest` and git SHA
2. ✅ Build frontend Docker image with correct ALB URL baked in
3. ✅ Push images to ECR
4. ✅ Update ECS task definitions
5. ✅ Deploy both backend and frontend services
6. ✅ Wait for services to stabilize

## Access Your Application

After deployment completes (usually 5-10 minutes):

- **Frontend**: http://transinia-dev-alb-1060895857.us-east-1.elb.amazonaws.com
- **Backend API**: http://transinia-dev-alb-1060895857.us-east-1.elb.amazonaws.com/api
- **Health Check**: http://transinia-dev-alb-1060895857.us-east-1.elb.amazonaws.com/api/health

## Frontend-Backend Connectivity Fix

### The Problem
Previously, the frontend was trying to connect to an old/wrong ALB DNS name, causing `ERR_NAME_NOT_RESOLVED` errors.

### The Solution
The workflow now:
1. Uses a hardcoded `ALB_DNS_NAME` environment variable
2. Passes it as build arguments to the frontend Docker build:
   ```yaml
   build-args: |
     NEXT_PUBLIC_BACKEND_URL=http://${{ env.ALB_DNS_NAME }}
     NEXT_PUBLIC_API_URL=http://${{ env.ALB_DNS_NAME }}/api
   ```
3. Next.js bakes this URL into the static files at build time

### Result
✅ Frontend always connects to the correct backend
✅ No more DNS resolution errors
✅ Upload, list, and fetch operations work correctly

## GitHub Secrets Required

Ensure these secrets are configured in your GitHub repository:

### AWS Credentials
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (e.g., `us-east-1`)
- `AWS_ACCOUNT_ID`

### OpenAI API
- `OPENAI_API_KEY`

### Dev Environment Resources
- `DEV_S3_BUCKET_RAW` (e.g., `transinia-dev-transcripts`)
- `DEV_S3_BUCKET_PROCESSED` (e.g., `transinia-dev-outputs`)
- `DEV_DYNAMODB_TABLE_MEETINGS` (e.g., `transinia-dev-meetings`)
- `DEV_DYNAMODB_TABLE_ACTIONS` (e.g., `transinia-dev-actions`)

### Prod Environment Resources (for future)
- `PROD_S3_BUCKET_RAW`
- `PROD_S3_BUCKET_PROCESSED`
- `PROD_DYNAMODB_TABLE_MEETINGS`
- `PROD_DYNAMODB_TABLE_ACTIONS`

## Monitoring Deployment

### Via GitHub Actions UI
1. Go to your repository's "Actions" tab
2. Select the workflow run
3. Watch the logs for each step

### Via AWS Console
**ECS Services:**
- Check task status: Running tasks should show as "RUNNING"
- Check deployment status: Should show "PRIMARY" deployment active

**CloudWatch Logs:**
- Backend logs: `/ecs/transinia-dev-backend`
- Frontend logs: `/ecs/transinia-dev-frontend`

**ALB Health:**
- Check target groups: Targets should be "healthy"

## Troubleshooting

### Frontend Can't Connect to Backend
1. Check ALB DNS name in workflow matches actual ALB
2. Verify ALB routing rules (Backend: `/api/*`, Frontend: `/*`)
3. Check backend service is running and healthy
4. Look at frontend container environment variables

### Service Won't Start
1. Check CloudWatch logs for errors
2. Verify task definition has correct IAM roles
3. Check security groups allow ALB → Tasks communication
4. Verify ECR images were pushed successfully

### Deployment Stuck
1. Check ECS service events for error messages
2. Verify task has sufficient CPU/memory
3. Check if tasks are failing health checks

## Rolling Back

### To Previous Version
Use the SHA-tagged images:
```bash
aws ecs update-service \
  --cluster transinia-dev-cluster \
  --service transinia-dev-backend-service \
  --task-definition transinia-dev-backend:PREVIOUS_REVISION
```

### Complete Rollback
Re-run GitHub Actions with a previous commit SHA.

## Cleanup

### Destroy All Infrastructure
⚠️ **Warning**: This will delete everything!

```bash
# Destroy ECS infrastructure
cd backend/infra/ecs-fargate-infra
terraform destroy

# Destroy databases
cd ../dynamodb-infra
terraform destroy

# Destroy S3 buckets
cd ../s3-bucket-infra
terraform destroy
```

## Production Deployment

When ready for production:
1. Update `.github/workflows/deploy-prod.yml` with prod ALB DNS
2. Deploy prod infrastructure using Terraform with `env=prod`
3. Push to `main` branch to trigger prod deployment

## Support

For issues or questions:
1. Check CloudWatch logs first
2. Review ECS service events
3. Verify GitHub Actions workflow logs
4. Check this guide for common solutions
