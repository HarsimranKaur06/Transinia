# Destroy Production Infrastructure
# Script to destroy Terraform-managed resources in the production environment

Write-Host "WARNING: You are about to destroy PRODUCTION infrastructure!" -ForegroundColor Red
$confirm = Read-Host "Are you sure you want to continue? (y/N)"

if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Operation cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host "Destroying production infrastructure..." -ForegroundColor Yellow

# Navigate to the S3 bucket infrastructure directory and destroy resources
Write-Host "Destroying S3 bucket infrastructure..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\backend\infra\s3-bucket-infra"
terraform init -upgrade
terraform destroy -auto-approve -var="environment=prod"

# Navigate to the DynamoDB infrastructure directory and destroy resources
Write-Host "Destroying DynamoDB infrastructure..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\backend\infra\dynamodb-infra"
terraform init -upgrade
terraform destroy -auto-approve -var="environment=prod"

Write-Host "Production infrastructure destruction completed!" -ForegroundColor Green