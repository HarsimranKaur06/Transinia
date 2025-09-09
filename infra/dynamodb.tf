# DynamoDB Table for Transinia Meeting Data
resource "aws_dynamodb_table" "transinia_meetings" {
  name           = "transinia-meetings"
  billing_mode   = "PAY_PER_REQUEST"  # On-demand capacity
  hash_key       = "meeting_id"
  range_key      = "date"

  attribute {
    name = "meeting_id"
    type = "S"
  }

  attribute {
    name = "date"
    type = "S"
  }

  attribute {
    name = "participants"
    type = "S"
  }

  # Global Secondary Index for querying by participant
  global_secondary_index {
    name               = "participant-index"
    hash_key           = "participants"
    projection_type    = "ALL"
  }

  # Tags
  tags = {
    Name        = "transinia-meetings"
    Environment = "production"
    Project     = "Transinia"
  }
}
