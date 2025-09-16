#!/bin/bash
# Script to create or destroy DynamoDB tables using Terraform and .env values

# Set script to exit on error
set -e

# Script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ENV_FILE="$SCRIPT_DIR/../../.env"
TERRAFORM_DIR="$SCRIPT_DIR"

# Function to read .env file and extract a value
get_env_value() {
  local key=$1
  grep "^$key=" "$ENV_FILE" | cut -d '=' -f2
}

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: .env file not found at $ENV_FILE"
  exit 1
fi

# Read values from .env
AWS_ACCESS_KEY_ID=$(get_env_value "AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=$(get_env_value "AWS_SECRET_ACCESS_KEY")
AWS_REGION=$(get_env_value "AWS_REGION")
DYNAMODB_TABLE_MEETINGS=$(get_env_value "DYNAMODB_TABLE_MEETINGS")
DYNAMODB_TABLE_ACTIONS=$(get_env_value "DYNAMODB_TABLE_ACTIONS")

# Check if required values are present
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$AWS_REGION" ]; then
  echo "Error: AWS credentials or region missing in .env file"
  exit 1
fi

if [ -z "$DYNAMODB_TABLE_MEETINGS" ] || [ -z "$DYNAMODB_TABLE_ACTIONS" ]; then
  echo "Warning: DynamoDB table names missing in .env file, using defaults"
  DYNAMODB_TABLE_MEETINGS="meeting-bot-meetings"
  DYNAMODB_TABLE_ACTIONS="meeting-bot-actions"
fi

# Create terraform.tfvars file
cat > "$TERRAFORM_DIR/terraform.tfvars" << EOL
aws_region = "$AWS_REGION"
aws_access_key_id = "$AWS_ACCESS_KEY_ID"
aws_secret_access_key = "$AWS_SECRET_ACCESS_KEY"
dynamodb_table_meetings = "$DYNAMODB_TABLE_MEETINGS"
dynamodb_table_actions = "$DYNAMODB_TABLE_ACTIONS"
environment = "dev"
project = "Transinia"
EOL

# Change to Terraform directory
cd "$TERRAFORM_DIR"

# Parse command line arguments
ACTION=${1:-"apply"}

if [ "$ACTION" == "apply" ] || [ "$ACTION" == "create" ]; then
  echo "Creating DynamoDB tables..."
  terraform init
  terraform apply -auto-approve
  echo "DynamoDB tables created successfully!"
  
elif [ "$ACTION" == "destroy" ] || [ "$ACTION" == "delete" ]; then
  echo "Destroying DynamoDB tables..."
  terraform init
  terraform destroy -auto-approve
  echo "DynamoDB tables destroyed successfully!"
  
else
  echo "Invalid action. Use 'apply'/'create' or 'destroy'/'delete'"
  exit 1
fi

# Clean up sensitive information
rm -f terraform.tfvars

echo "Done!"
