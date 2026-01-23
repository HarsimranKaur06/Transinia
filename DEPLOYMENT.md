# README: Pushing to Production and Managing Environments

This document provides instructions for managing both development and production environments for the Transinia application.

## Deployment Architecture

**Infrastructure**: Manually deployed using Terraform (one-time setup)
**Application**: Automatically deployed via GitHub Actions

## GitHub Workflow Setup

The project is configured with two GitHub Actions workflows:

1. **Development Workflow** (`deploy-dev.yml`)
   - Triggers automatically when changes are pushed to the `dev` branch
   - Deploys **application only** (backend + frontend Docker containers)
   - Assumes infrastructure (S3, DynamoDB, ECS cluster, ALB) already exists
   - Used for testing and development purposes

2. **Production Workflow** (`deploy-prod.yml`) 
   - Triggers automatically when changes are pushed to the `main` branch
   - Can also be triggered manually from the GitHub Actions tab
   - Deploys **application only** (backend + frontend Docker containers)
   - Assumes infrastructure already exists
   - Used for the production/live version of the application

## Prerequisites

Before deploying applications, ensure infrastructure is set up:

1. Deploy infrastructure manually using Terraform (see `backend/infra/` directories)
2. Configure GitHub Secrets with infrastructure details (ALB DNS, S3 buckets, DynamoDB tables)
3. Verify ECS cluster, services, and task definitions exist

See `DEPLOYMENT_GUIDE.md` for detailed infrastructure setup instructions.

## Deploying Applications to Production

To deploy application code to production:

1. Ensure all changes have been tested in the development environment
2. Create a pull request from `dev` to `main`
3. Review and approve the pull request
4. Merge the pull request to trigger the production workflow

The workflow will:
- Build backend and frontend Docker images
- Push images to ECR
- Update ECS task definitions
- Deploy to ECS Fargate

Alternatively, you can manually trigger a production deployment:
1. Go to the GitHub repository
2. Click the "Actions" tab
3. Select "Deploy Infrastructure (prod)" workflow
4. Click "Run workflow"
5. Click "Run workflow" to confirm

## Managing Infrastructure

### Viewing Infrastructure

To view the current infrastructure state:

```bash
# For development
cd backend/infra/s3-bucket-infra
terraform init
terraform show

cd ../dynamodb-infra
terraform init
terraform show

cd ../ecs-fargate-infra
terraform init
terraform show
```

### Destroying Infrastructure

⚠️ **Warning**: Destroying infrastructure will delete all resources including data in S3 and DynamoDB!

Destroy in reverse order:

```bash
# 1. Destroy ECS infrastructure first
cd backend/infra/ecs-fargate-infra
terraform destroy -var-file="terraform.tfvars"

# 2. Destroy DynamoDB tables
cd ../dynamodb-infra
terraform destroy -var-file="terraform.tfvars"

# 3. Destroy S3 buckets last
cd ../s3-bucket-infra
terraform destroy -var-file="terraform.tfvars"
```

## Important Notes

1. **Infrastructure must be deployed manually first** before application deployments work
2. **Always test changes in development first** before pushing to production
3. **GitHub Secrets must match Terraform outputs** (ALB DNS, S3 buckets, DynamoDB tables)
4. **Use caution when destroying production infrastructure** - data loss is permanent
5. **Workflows only deploy application code**, not infrastructure

## Troubleshooting

If workflows fail:
1. **Check infrastructure exists**: Verify ECS cluster, services, ALB, ECR repos exist in AWS Console
2. **Verify GitHub Secrets**: Ensure all environment-specific secrets are configured correctly
3. **Check AWS credentials**: Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY have correct permissions
4. **Review GitHub Actions logs**: Look for specific error messages in workflow runs
5. **Check ECS service health**: Verify tasks are running and healthy in ECS console