# Environment settings
env = "prod"
aws_region = "us-east-1"

# Application settings
app_name = "transinia"

# S3 bucket base names
s3_bucket_raw = "transcripts"
s3_bucket_processed = "outputs"

# ALB DNS for CORS - Leave empty, will be set by GitHub Actions workflow
alb_dns_name = ""

# CORS allowed origins - localhost for local development
allowed_origins = [
  "http://localhost:3000",
  "http://localhost:5000"
]