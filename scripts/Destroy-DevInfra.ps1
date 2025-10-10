# Destroy Development Infrastructure
# Script to destroy Terraform-managed resources in the development environment

Write-Host "Destroying development infrastructure..." -ForegroundColor Yellow

# Check if AWS credentials are set in environment
if (-not $env:AWS_ACCESS_KEY_ID -or -not $env:AWS_SECRET_ACCESS_KEY) {
    Write-Host "AWS credentials not found in environment. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY." -ForegroundColor Red
    Write-Host "Example:" -ForegroundColor Yellow
    Write-Host '$env:AWS_ACCESS_KEY_ID = "your-access-key"' -ForegroundColor Cyan
    Write-Host '$env:AWS_SECRET_ACCESS_KEY = "your-secret-key"' -ForegroundColor Cyan
    exit 1
}

# Navigate to the S3 bucket infrastructure directory and destroy resources
Write-Host "Destroying S3 bucket infrastructure..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\backend\infra\s3-bucket-infra"
terraform init -upgrade
terraform destroy -auto-approve -var="environment=dev"

# Navigate to the DynamoDB infrastructure directory and destroy resources
Write-Host "Destroying DynamoDB infrastructure..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\backend\infra\dynamodb-infra"
terraform init -upgrade
terraform destroy -auto-approve -var="environment=dev"

Write-Host "Development infrastructure destruction completed!" -ForegroundColor Green