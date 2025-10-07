/*
  MAIN TERRAFORM CONFIGURATION
  ---------------------------
  This file defines the core Terraform settings and backend configuration
  for the S3 bucket infrastructure.
*/

terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30"
    }
  }

  # Uncomment this section to enable remote state storage in S3
  # backend "s3" {
  #   bucket         = "transinia-terraform-state"
  #   key            = "s3-buckets/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-locks"
  # }
}

provider "aws" {
  region = "us-east-1"
}