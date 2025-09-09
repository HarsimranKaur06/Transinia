# DynamoDB Table for Transinia Meeting Data
resource "aws_dynamodb_table" "transinia_meetings" {
  name           = "meeting-bot-meetings"  # Updated to match current deployment
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
    Name        = "meeting-bot-meetings"
    Environment = "production"
    Project     = "Transinia"
  }
}

# DynamoDB Table for Transinia Action Items
resource "aws_dynamodb_table" "transinia_actions" {
  name           = "meeting-bot-actions"  # Updated to match current deployment
  billing_mode   = "PAY_PER_REQUEST"  # On-demand capacity
  hash_key       = "action_id"
  range_key      = "meeting_id"

  attribute {
    name = "action_id"
    type = "S"
  }

  attribute {
    name = "meeting_id"
    type = "S"
  }

  attribute {
    name = "owner"
    type = "S"
  }

  # Global Secondary Index for querying by owner
  global_secondary_index {
    name               = "owner-index"
    hash_key           = "owner"
    projection_type    = "ALL"
  }

  # Tags
  tags = {
    Name        = "meeting-bot-actions"
    Environment = "production"
    Project     = "Transinia"
  }
}
