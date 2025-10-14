/*
  S3 BUCKET INFRASTRUCTURE
  ------------------------
  This Terraform file creates and configures the S3 buckets needed by the Transinia application:
  
  1. Raw data bucket (meeting-bot-transcripts): Stores meeting transcripts
  2. Processed data bucket (meeting-bot-outputs): Stores meeting minutes and action items
  
  The configuration matches the existing buckets to ensure no code changes are required.
*/

# Raw transcripts bucket
resource "aws_s3_bucket" "raw_bucket" {
  bucket = local.s3_bucket_raw
  
  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix} Transcripts"
      Description = "Stores raw meeting transcripts for processing"
    }
  )
}

# Block public access
resource "aws_s3_bucket_public_access_block" "raw_bucket_public_access_block" {
  bucket = aws_s3_bucket.raw_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Configure bucket properties
resource "aws_s3_bucket_ownership_controls" "raw_bucket_ownership" {
  bucket = aws_s3_bucket.raw_bucket.id
  
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "raw_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.raw_bucket_ownership,
    aws_s3_bucket_public_access_block.raw_bucket_public_access_block,
  ]
  
  bucket = aws_s3_bucket.raw_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "raw_bucket_versioning" {
  bucket = aws_s3_bucket.raw_bucket.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable CORS for raw bucket
resource "aws_s3_bucket_cors_configuration" "raw_bucket_cors" {
  bucket = aws_s3_bucket.raw_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_origins = ["*"]  # In production, restrict this to your domain
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Processed outputs bucket
resource "aws_s3_bucket" "processed_bucket" {
  bucket = local.s3_bucket_processed
  
  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix} Outputs"
      Description = "Stores processed meeting minutes and action items"
    }
  )
}

# Block public access
resource "aws_s3_bucket_public_access_block" "processed_bucket_public_access_block" {
  bucket = aws_s3_bucket.processed_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Configure bucket properties
resource "aws_s3_bucket_ownership_controls" "processed_bucket_ownership" {
  bucket = aws_s3_bucket.processed_bucket.id
  
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "processed_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.processed_bucket_ownership,
    aws_s3_bucket_public_access_block.processed_bucket_public_access_block,
  ]
  
  bucket = aws_s3_bucket.processed_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "processed_bucket_versioning" {
  bucket = aws_s3_bucket.processed_bucket.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable CORS for processed bucket
resource "aws_s3_bucket_cors_configuration" "processed_bucket_cors" {
  bucket = aws_s3_bucket.processed_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_origins = ["*"]  # In production, restrict this to your domain
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Create empty folders in raw bucket
resource "aws_s3_object" "raw_transcripts_folder" {
  bucket  = aws_s3_bucket.raw_bucket.id
  key     = "transcripts/"
  content_type = "application/x-directory"
}

# Create empty folders in processed bucket
resource "aws_s3_object" "processed_minutes_folder" {
  bucket  = aws_s3_bucket.processed_bucket.id
  key     = "minutes/"
  content_type = "application/x-directory"
}

resource "aws_s3_object" "processed_actions_folder" {
  bucket  = aws_s3_bucket.processed_bucket.id
  key     = "actions/"
  content_type = "application/x-directory"
}

resource "aws_s3_object" "processed_meeting_data_folder" {
  bucket  = aws_s3_bucket.processed_bucket.id
  key     = "meeting_data/"
  content_type = "application/x-directory"
}

# Outputs are defined in outputs.tf