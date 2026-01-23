# Production Deployment Guide

This guide outlines the steps to deploy the Transinia application to the production environment.

## Overview

**Deployment Model:**
- Infrastructure: Manually deployed using Terraform
- Application: Automatically deployed via GitHub Actions

## Prerequisites

1. GitHub repository with both `dev` and `main` branches
2. AWS account with appropriate IAM permissions
3. Terraform installed locally
4. GitHub repository secrets configured (see below)

## Required GitHub Secrets for Production

Before deploying to production, ensure these secrets are set in your GitHub repository (Settings → Secrets and variables → Actions):

### Common Secrets (Used in both Dev and Prod)
- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_REGION`: The AWS region for deployment (e.g., us-east-1)
- `AWS_ACCOUNT_ID`: Your AWS account ID
- `OPENAI_API_KEY`: Your OpenAI API key

### Development-Specific Secrets
- `DEV_ALB_DNS_NAME`: Dev ALB DNS from Terraform output
- `DEV_S3_BUCKET_RAW`: Dev raw transcripts bucket name (e.g., `transinia-dev-transcripts`)
- `DEV_S3_BUCKET_PROCESSED`: Dev processed outputs bucket name (e.g., `transinia-dev-outputs`)
- `DEV_DYNAMODB_TABLE_MEETINGS`: Dev meetings table name (e.g., `transinia-dev-meetings`)
- `DEV_DYNAMODB_TABLE_ACTIONS`: Dev actions table name (e.g., `transinia-dev-actions`)

### Production-Specific Secrets
- `PROD_ALB_DNS_NAME`: Prod ALB DNS from Terraform output
- `PROD_S3_BUCKET_RAW`: Prod raw transcripts bucket name (e.g., `transinia-prod-transcripts`)
- `PROD_S3_BUCKET_PROCESSED`: Prod processed outputs bucket name (e.g., `transinia-prod-outputs`)
- `PROD_DYNAMODB_TABLE_MEETINGS`: Prod meetings table name (e.g., `transinia-prod-meetings`)
- `PROD_DYNAMODB_TABLE_ACTIONS`: Prod actions table name (e.g., `transinia-prod-actions`)

## Deployment Steps

### 1. Initial Production Infrastructure Setup (Manual)

Deploy the infrastructure for production using Terraform:

```bash
# Clone the repository if you haven't already
git clone https://github.com/HarsimranKaur06/Transinia.git
cd Transinia

# Checkout the main branch
git checkout main

# Deploy S3 infrastructure
cd backend/infra/s3-bucket-infra
terraform init
terraform plan -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars"

# Get S3 bucket names
terraform output raw_bucket_name
terraform output processed_bucket_name

# Deploy DynamoDB infrastructure
cd ../dynamodb-infra
terraform init
terraform plan -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars"

# Get DynamoDB table names
terraform output meetings_table_name
terraform output actions_table_name

# Deploy ECS Fargate infrastructure
cd ../ecs-fargate-infra
terraform init
terraform plan -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars"

# Get ALB DNS name
terraform output alb_dns_name
```

### 2. Configure GitHub Secrets

Add the Terraform output values to GitHub Secrets:
- Go to repository Settings → Secrets and variables → Actions
- Add `PROD_ALB_DNS_NAME`, `PROD_S3_BUCKET_RAW`, `PROD_S3_BUCKET_PROCESSED`, `PROD_DYNAMODB_TABLE_MEETINGS`, `PROD_DYNAMODB_TABLE_ACTIONS`

### 3. Deploy Application via GitHub Actions

Once infrastructure is set up and secrets are configured, the application will deploy automatically:

**Option 1: Automatic Deployment**

1. Test your changes in the development environment first:
   ```bash
   git checkout dev
   # Make your changes
   git add .
   git commit -m "Your changes"
   git push origin dev
   ```

2. Create a pull request from `dev` to `main` in GitHub

3. Review the changes and ensure all tests pass

4. Merge the pull request - this triggers automatic application deployment to production

5. Monitor the GitHub Actions workflow in the "Actions" tab of your repository

**Option 2: Manual Deployment**

You can trigger the production deployment workflow manually:

1. Go to the "Actions" tab in your GitHub repository
2. Select "Deploy Infrastructure (prod)"
3. Click "Run workflow"
4. Click "Run workflow" to confirm

## Verifying the Deployment

After deployment, verify that your resources were created properly:

```bash
# Check S3 buckets
aws s3 ls | grep transinia-prod

# Check DynamoDB tables
aws dynamodb list-tables | grep transinia-prod

# Check ECS services
aws ecs describe-services --cluster transinia-prod-cluster --services transinia-prod-backend-service transinia-prod-frontend-service
```

## Destroying Production Infrastructure

⚠️ **Warning**: This will permanently delete all production resources and data!

Destroy infrastructure in reverse order:

```bash
cd backend/infra/ecs-fargate-infra
terraform destroy -var-file="prod.tfvars"

cd ../dynamodb-infra
terraform destroy -var-file="prod.tfvars"

cd ../s3-bucket-infra
terraform destroy -var-file="prod.tfvars"
```

## Troubleshooting

If you encounter issues with the deployment:

1. Check the GitHub Actions logs for error messages
2. Verify that all required secrets are set correctly
3. Check AWS CloudWatch logs for the ECS services
4. Ensure the IAM user has all required permissions