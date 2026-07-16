//Added for setting up prometheus monitoring
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1" // Change as needed
}
