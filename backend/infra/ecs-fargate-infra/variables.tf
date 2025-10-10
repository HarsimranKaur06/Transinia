variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "app_name" {
  type    = string
  default = "transinia"
}

variable "env" {
  type    = string
  default = "dev"
}

variable "environment" {
  type    = string
  default = "dev"
  description = "Environment name for resources (prod, dev, etc.)"
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

# Health check paths (change if your backend uses /api/health)
variable "backend_health_check_path" {
  type    = string
  default = "/health"
}

variable "frontend_health_check_path" {
  type    = string
  default = "/"
}

# Existing S3 buckets (from your .env)
variable "s3_bucket_raw" {
  type    = string
  default = "meeting-bot-transcripts"
}

variable "s3_bucket_processed" {
  type    = string
  default = "meeting-bot-outputs"
}

# DynamoDB table base names
variable "dynamodb_table_meetings_base" {
  type    = string
  default = "meetings"
  description = "Base name for meetings DynamoDB table, will be prefixed with transinia-{env}-"
}

variable "dynamodb_table_actions_base" {
  type    = string
  default = "actions"
  description = "Base name for actions DynamoDB table, will be prefixed with transinia-{env}-"
}

# For backward compatibility
variable "dynamodb_table_meetings" {
  type    = string
  default = ""
  description = "Full name of meetings table (deprecated, use dynamodb_table_meetings_base instead)"
}

variable "dynamodb_table_actions" {
  type    = string
  default = ""
  description = "Full name of actions table (deprecated, use dynamodb_table_actions_base instead)"
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
