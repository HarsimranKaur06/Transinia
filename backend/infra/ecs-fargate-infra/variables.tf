variable "aws_region" {
  type        = string
  description = "AWS region for resources"
  default     = "us-east-1"
}

variable "app_name" {
  type        = string
  description = "Application name"
  default     = "transinia"
}

variable "env" {
  type        = string
  description = "Environment (dev/prod)"
  default     = "dev"
}

variable "s3_bucket_raw" {
  type        = string
  description = "Name for raw S3 bucket"
  default     = "transcripts"
}

variable "s3_bucket_processed" {
  type        = string
  description = "Name for processed S3 bucket"
  default     = "outputs"
}

variable "dynamodb_table_meetings" {
  type        = string
  description = "Name for meetings DynamoDB table"
  default     = "meetings"
}

variable "dynamodb_table_actions" {
  type        = string
  description = "Name for actions DynamoDB table"
  default     = "actions"
}

# VPC CIDRs
variable "vpc_cidr" {
  type    = string
  default = "10.40.0.0/16"
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.40.1.0/24", "10.40.2.0/24"]
}

variable "private_subnet_cidrs" {
  type    = list(string)
  default = ["10.40.11.0/24", "10.40.12.0/24"]
}

# Container ports
variable "backend_container_port" {
  type    = number
  default = 8001
}

variable "frontend_container_port" {
  type    = number
  default = 3000
}

# Control resource creation
variable "create_cloudwatch_log_groups" {
  type        = bool
  default     = true
  description = "Whether to create CloudWatch log groups or assume they already exist"
}

variable "create_vpc_resources" {
  type        = bool
  default     = true
  description = "Whether to create VPC and related resources or assume they already exist"
}

variable "create_alb_resources" {
  type        = bool
  default     = true
  description = "Whether to create ALB and related resources or assume they already exist"
}

variable "create_iam_resources" {
  type        = bool
  default     = true
  description = "Whether to create IAM roles and policies or assume they already exist"
}

variable "create_security_groups" {
  type        = bool
  default     = true
  description = "Whether to create security groups or assume they already exist"
}

# Health check paths (change if your backend uses /api/health)
variable "backend_health_check_path" {
  type    = string
  default = "/health"
}

variable "frontend_health_check_path" {
  type    = string
  default = "/"
}

# Existing S3 buckets - using environment-based naming
variable "s3_bucket_raw" {
  type        = string
  description = "Raw transcripts S3 bucket name"
  default     = "transinia-dev-transcripts"  # Will be overridden per environment
}

variable "s3_bucket_processed" {
  type        = string
  description = "Processed outputs S3 bucket name"
  default     = "transinia-dev-outputs"  # Will be overridden per environment
}

# Existing DynamoDB tables - using environment-based naming
variable "dynamodb_table_meetings" {
  type        = string
  description = "Meetings DynamoDB table name"
  default     = "transinia-dev-meetings"  # Will be overridden per environment
}

variable "dynamodb_table_actions" {
  type        = string
  description = "Actions DynamoDB table name"
  default     = "transinia-dev-actions"  # Will be overridden per environment
}

# App envs from .env (no secrets here)
variable "use_dynamodb" {
  type    = bool
  default = true
}

variable "log_level" {
  type    = string
  default = "INFO"
}

# Initial placeholder images (GitHub Actions will roll new images on deploy)
variable "backend_image" {
  type    = string
  default = "public.ecr.aws/docker/library/nginx:alpine"
}

variable "frontend_image" {
  type    = string
  default = "public.ecr.aws/docker/library/nginx:alpine"
}

# Desired task counts
variable "backend_desired_count" {
  type    = number
  default = 1
}

variable "frontend_desired_count" {
  type    = number
  default = 1
}
