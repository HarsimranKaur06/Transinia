# S3 Bucket Infrastructure

This directory contains Terraform configurations for managing S3 buckets required by Transinia.

## S3 Buckets

The `s3_buckets.tf` file creates and configures the S3 buckets needed by the application:

- **meeting-bot-transcripts**: Raw transcript storage
- **meeting-bot-outputs**: Processed meeting minutes and action items

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) (v1.0.0+)
- AWS CLI configured with appropriate credentials
- An AWS account with permissions to create S3 resources

## Usage

To apply this Terraform configuration:

```bash
# Navigate to this directory
cd backend/infra/s3-bucket-infra

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply changes
terraform apply

# When you want to destroy resources
terraform destroy
```

## Replacing Existing Buckets

If you want to replace existing manually-created buckets with these Terraform-managed buckets:

1. Make sure you have a backup of any important data in the existing buckets
2. Delete the existing buckets in AWS console
3. Run `terraform apply` to create new buckets with identical names
4. Restore your data if needed

## Important Notes

- This Terraform configuration uses the exact same bucket names as the current application expects, so no code changes are required.
- The bucket names are hardcoded rather than using variables to ensure they match the existing application configuration.
- Versioning is enabled on both buckets to prevent accidental data loss.
- Empty folders (prefixes) are created to match the expected structure.

## Integration with ECS

For the complete infrastructure, you may want to integrate this with your ECS Terraform configuration. The bucket ARNs are provided as outputs that can be used in IAM policies.