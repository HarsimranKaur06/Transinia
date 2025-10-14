# README: Pushing to Production and Managing Environments

This document provides instructions for managing both development and production environments for the Transinia application.

## GitHub Workflow Setup

The project is configured with two GitHub Actions workflows:

1. **Development Workflow** (`deploy-dev.yml`)
   - Triggers automatically when changes are pushed to the `dev` branch
   - Deploys resources with the environment tag "dev"
   - Used for testing and development purposes

2. **Production Workflow** (`deploy-prod.yml`) 
   - Triggers automatically when changes are pushed to the `main` branch
   - Can also be triggered manually from the GitHub Actions tab
   - Deploys resources with the environment tag "prod"
   - Used for the production/live version of the application

## Deploying to Production

To deploy to production:

1. Ensure all changes have been tested in the development environment
2. Create a pull request from `dev` to `main`
3. Review and approve the pull request
4. Merge the pull request to trigger the production workflow

Alternatively, you can manually trigger a production deployment:
1. Go to the GitHub repository
2. Click the "Actions" tab
3. Select "CI/CD — build, push to ECR, deploy to ECS (production)" workflow
4. Click "Run workflow"
5. Enter a reason for the manual deployment and click "Run workflow"

## Managing Infrastructure

### Viewing Infrastructure

To view the current infrastructure state:

```bash
# For development
cd backend/infra/s3-bucket-infra
terraform init
terraform show

cd backend/infra/dynamodb-infra
terraform init
terraform show
```

### Destroying Infrastructure

When you need to destroy the infrastructure, use the provided scripts:

**For Windows PowerShell:**
```powershell
# Destroy development infrastructure
.\scripts\Destroy-DevInfra.ps1

# Destroy production infrastructure (includes confirmation)
.\scripts\Destroy-ProdInfra.ps1
```

**For Bash:**
```bash
# Destroy development infrastructure
bash ./scripts/destroy-dev-infra.sh

# Destroy production infrastructure (includes confirmation)
bash ./scripts/destroy-prod-infra.sh
```

## Important Notes

1. **Always test changes in development first** before pushing to production
2. **Use caution when destroying production infrastructure**
3. **Environment variables** in the workflows should be configured in GitHub repository secrets

## Troubleshooting

If workflows fail:
1. Check GitHub Actions logs for detailed error messages
2. Verify AWS credentials are properly set in GitHub secrets
3. Ensure all required environment variables are present