# Production Deployment Guide

This guide outlines the steps to deploy the Transinia application to the production environment.

## Prerequisites

1. GitHub repository with both `dev` and `main` branches
2. AWS account with appropriate permissions
3. GitHub repository secrets configured (see below)

## Required GitHub Secrets for Production

Before deploying to production, ensure these secrets are set in your GitHub repository:

### Common Secrets (Used in both Dev and Prod)
- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_REGION`: The AWS region for deployment (e.g., us-east-1)
- `AWS_ACCOUNT_ID`: Your AWS account ID
- `OPENAI_API_KEY`: Your OpenAI API key

### Development-Specific Secrets
- `DEV_DYNAMODB_TABLE_MEETINGS_BASE`: Base name for dev meetings table (e.g., "meetings")
- `DEV_DYNAMODB_TABLE_ACTIONS_BASE`: Base name for dev actions table (e.g., "actions")
- `DEV_S3_BUCKET_RAW_BASE`: Base name for dev raw data bucket (e.g., "transcripts")
- `DEV_S3_BUCKET_PROCESSED_BASE`: Base name for dev processed data bucket (e.g., "outputs")

### Production-Specific Secrets
- `PROD_DYNAMODB_TABLE_MEETINGS_BASE`: Base name for prod meetings table (e.g., "meetings")
- `PROD_DYNAMODB_TABLE_ACTIONS_BASE`: Base name for prod actions table (e.g., "actions")
- `PROD_S3_BUCKET_RAW_BASE`: Base name for prod raw data bucket (e.g., "transcripts")
- `PROD_S3_BUCKET_PROCESSED_BASE`: Base name for prod processed data bucket (e.g., "outputs")

## Deployment Steps

### 1. Initial Production Infrastructure Setup

To deploy the infrastructure for production for the first time:

```bash
# Clone the repository if you haven't already
git clone https://github.com/HarsimranKaur06/Transinia.git
cd Transinia

# Checkout the main branch
git checkout main

# Deploy S3 infrastructure manually
cd backend/infra/s3-bucket-infra
terraform init
terraform plan -out=s3_tf.plan -var="environment=prod" \
  -var="s3_bucket_raw=${PROD_S3_BUCKET_RAW_BASE}" \
  -var="s3_bucket_processed=${PROD_S3_BUCKET_PROCESSED_BASE}"
terraform apply -auto-approve s3_tf.plan

# Deploy DynamoDB infrastructure manually
cd ../dynamodb-infra
terraform init
terraform plan -out=dynamodb_tf.plan -var="environment=prod" \
  -var="dynamodb_table_meetings=${PROD_DYNAMODB_TABLE_MEETINGS_BASE}" \
  -var="dynamodb_table_actions=${PROD_DYNAMODB_TABLE_ACTIONS_BASE}"
terraform apply -auto-approve dynamodb_tf.plan
```

### 2. Ongoing Deployments via GitHub Actions

Once the initial setup is complete, future deployments to production will happen automatically when changes are merged to the `main` branch:

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

4. Merge the pull request to deploy to production

5. Monitor the GitHub Actions workflow in the "Actions" tab of your repository

### 3. Manual Production Deployment (if needed)

You can also trigger the production deployment workflow manually:

1. Go to the "Actions" tab in your GitHub repository
2. Select "CI/CD — build, push to ECR, deploy to ECS (production)"
3. Click "Run workflow"
4. Enter a reason for the deployment and click "Run workflow"

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

## Destroying Infrastructure When Not Needed

To destroy the production infrastructure:

```bash
# Run the provided script
cd Transinia
./scripts/Destroy-ProdInfra.ps1  # For Windows
# OR
bash ./scripts/destroy-prod-infra.sh  # For Linux/Mac
```

## Troubleshooting

If you encounter issues with the deployment:

1. Check the GitHub Actions logs for error messages
2. Verify that all required secrets are set correctly
3. Check AWS CloudWatch logs for the ECS services
4. Ensure the IAM user has all required permissions