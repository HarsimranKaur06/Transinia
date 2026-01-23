# GitHub Secrets Configuration

This document lists all the GitHub Secrets that need to be configured for the CI/CD workflows to work properly.

## How to Add Secrets

1. Go to your GitHub repository: `https://github.com/HarsimranKaur06/Transinia`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret listed below

---

## Required Secrets

### AWS Credentials (Shared across environments)

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `AWS_ACCOUNT_ID` | Your AWS Account ID | `123456789012` |
| `AWS_REGION` | AWS Region for deployment | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS IAM Access Key ID | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM Secret Access Key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `OPENAI_API_KEY` | OpenAI API Key for backend | `sk-proj-XXXXXXXXXXXXXXXXXXXXXXXX` |

---

### Dev Environment Secrets

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `DEV_ALB_DNS_NAME` | Dev ALB DNS Name | `transinia-dev-alb-1060895857.us-east-1.elb.amazonaws.com` |
| `DEV_S3_BUCKET_RAW` | Dev S3 bucket for raw transcripts | `transinia-dev-transcripts` |
| `DEV_S3_BUCKET_PROCESSED` | Dev S3 bucket for processed outputs | `transinia-dev-outputs` |
| `DEV_DYNAMODB_TABLE_MEETINGS` | Dev DynamoDB meetings table | `transinia-dev-meetings` |
| `DEV_DYNAMODB_TABLE_ACTIONS` | Dev DynamoDB actions table | `transinia-dev-actions` |

---

### Prod Environment Secrets

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `PROD_ALB_DNS_NAME` | Prod ALB DNS Name | `transinia-prod-alb-XXXXXXXXXX.us-east-1.elb.amazonaws.com` |
| `PROD_S3_BUCKET_RAW` | Prod S3 bucket for raw transcripts | `transinia-prod-transcripts` |
| `PROD_S3_BUCKET_PROCESSED` | Prod S3 bucket for processed outputs | `transinia-prod-outputs` |
| `PROD_DYNAMODB_TABLE_MEETINGS` | Prod DynamoDB meetings table | `transinia-prod-meetings` |
| `PROD_DYNAMODB_TABLE_ACTIONS` | Prod DynamoDB actions table | `transinia-prod-actions` |

---

## Current Values Reference

### Dev Environment (To Be Set After Infrastructure Setup)
```bash
# TODO: Update these after running Terraform for prod
DEV_ALB_DNS_NAME=<your-dev-alb-dns>
DEV_S3_BUCKET_RAW=transinia-dev-transcripts
DEV_S3_BUCKET_PROCESSED=transinia-dev-outputs
DEV_DYNAMODB_TABLE_MEETINGS=transinia-dev-meetings
DEV_DYNAMODB_TABLE_ACTIONS=transinia-dev-actions
```

### Prod Environment (To Be Set After Infrastructure Setup)
```bash
# TODO: Update these after running Terraform for prod
PROD_ALB_DNS_NAME=<your-prod-alb-dns>
PROD_S3_BUCKET_RAW=transinia-prod-transcripts
PROD_S3_BUCKET_PROCESSED=transinia-prod-outputs
PROD_DYNAMODB_TABLE_MEETINGS=transinia-prod-meetings
PROD_DYNAMODB_TABLE_ACTIONS=transinia-prod-actions
```

---

## Setting Up Dev and Prod Infrastructure

After manually creating prod infrastructure using Terraform:

1. Run Terraform in `backend/infra/` directories to create:
   - S3 buckets
   - DynamoDB tables
   - ECS Fargate cluster
   - Application Load Balancer
   - IAM roles

2. Get the ALB DNS name from Terraform outputs:
   ```bash
   terraform output alb_dns_name
   ```

3. Add all prod secrets to GitHub

4. Push to `main` branch to trigger prod deployment

---

## Workflow Triggers

- **Dev Deployment**: Push to `dev` branch or manual workflow dispatch
- **Prod Deployment**: Push to `main` branch or manual workflow dispatch

---

## Verification

After adding secrets, verify they're correctly set:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. You should see all secrets listed (values are hidden)
3. Trigger a workflow run to test

---

## Security Notes

**IMPORTANT:**
- Never commit secrets to the repository
- Use separate AWS credentials for dev and prod (recommended)
- Rotate credentials regularly
- Use IAM roles with minimal required permissions
- Keep OpenAI API keys secure with usage limits
