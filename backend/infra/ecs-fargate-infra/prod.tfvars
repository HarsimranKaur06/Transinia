# Environment settings
env = "prod"
aws_region = "us-east-1"

# Application settings
app_name = "transinia"

# Base names for resources
s3_bucket_raw = "transcripts"
s3_bucket_processed = "outputs"
dynamodb_table_meetings = "meetings"
dynamodb_table_actions = "actions"

# Container ports
backend_container_port = 8001
frontend_container_port = 3000