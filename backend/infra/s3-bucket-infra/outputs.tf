/*
  TERRAFORM OUTPUTS
  ----------------
  This file defines the outputs from the S3 bucket infrastructure.
*/

output "raw_bucket_arn" {
  description = "ARN of the raw transcripts bucket"
  value       = aws_s3_bucket.raw_bucket.arn
}

output "raw_bucket_name" {
  description = "Name of the raw transcripts bucket"
  value       = aws_s3_bucket.raw_bucket.id
}

output "processed_bucket_arn" {
  description = "ARN of the processed outputs bucket"
  value       = aws_s3_bucket.processed_bucket.arn
}

output "processed_bucket_name" {
  description = "Name of the processed outputs bucket"
  value       = aws_s3_bucket.processed_bucket.id
}