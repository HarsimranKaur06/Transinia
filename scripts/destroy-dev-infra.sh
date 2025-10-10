#!/bin/bash
# destroy-dev-infra.sh
# Script to destroy development infrastructure

echo "Destroying development infrastructure..."

# Check if AWS credentials are set in environment
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "AWS credentials not found in environment. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
  echo "Example:"
  echo "export AWS_ACCESS_KEY_ID=\"your-access-key\""
  echo "export AWS_SECRET_ACCESS_KEY=\"your-secret-key\""
  exit 1
fi

# Navigate to the S3 bucket infrastructure directory and destroy resources
echo "Destroying S3 bucket infrastructure..."
cd "$(dirname "$0")/../backend/infra/s3-bucket-infra"
terraform init -upgrade
terraform destroy -auto-approve -var="environment=dev"

# Navigate to the DynamoDB infrastructure directory and destroy resources
echo "Destroying DynamoDB infrastructure..."
cd "$(dirname "$0")/../backend/infra/dynamodb-infra"
terraform init -upgrade
terraform destroy -auto-approve -var="environment=dev"

echo "Development infrastructure destruction completed!"