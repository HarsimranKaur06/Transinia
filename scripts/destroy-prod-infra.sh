#!/bin/bash
# destroy-prod-infra.sh
# Script to destroy production infrastructure

echo "WARNING: You are about to destroy PRODUCTION infrastructure!"
read -p "Are you sure you want to continue? (y/N): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Operation cancelled."
  exit 0
fi

echo "Destroying production infrastructure..."

# Navigate to the S3 bucket infrastructure directory and destroy resources
echo "Destroying S3 bucket infrastructure..."
cd "$(dirname "$0")/../backend/infra/s3-bucket-infra"
terraform init -upgrade
terraform destroy -auto-approve -var="environment=prod"

# Navigate to the DynamoDB infrastructure directory and destroy resources
echo "Destroying DynamoDB infrastructure..."
cd "$(dirname "$0")/../backend/infra/dynamodb-infra"
terraform init -upgrade
terraform destroy -auto-approve -var="environment=prod"

echo "Production infrastructure destruction completed!"