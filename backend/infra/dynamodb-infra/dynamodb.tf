# dynamodb.tf - DynamoDB tables for Transinia

# Meetings table - stores complete meeting records
resource "aws_dynamodb_table" "meetings" {
  name           = local.dynamodb_table_meetings
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

  # Participant search support
  attribute {
    name = "participant_key"
    type = "S"
  }

  # Due date search support
  attribute {
    name = "due_date"
    type = "S"
  }

  # Global Secondary Index for participant search
  global_secondary_index {
    name               = "participant-index"
    hash_key           = "participant_key"
    projection_type    = "ALL"
    write_capacity     = 0
    read_capacity      = 0
  }

  # Global Secondary Index for due date search
  global_secondary_index {
    name               = "due-date-index"
    hash_key           = "due_date"
    projection_type    = "ALL"
    write_capacity     = 0
    read_capacity      = 0
  }

  # Point-in-time recovery for data protection
  point_in_time_recovery {
    enabled = true
  }

  # Tags
  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix} Meetings Table"
    }
  )
}

# Actions table - stores individual action items for faster querying
resource "aws_dynamodb_table" "actions" {
  name           = local.dynamodb_table_actions
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

  # Owner search support
  attribute {
    name = "owner"
    type = "S"
  }

  # Priority and due date search
  attribute {
    name = "priority_due"
    type = "S"
  }

  # Global Secondary Index for owner search
  global_secondary_index {
    name               = "owner-index"
    hash_key           = "owner"
    range_key          = "meeting_id"
    projection_type    = "ALL"
    write_capacity     = 0
    read_capacity      = 0
  }

  # Global Secondary Index for priority and due date
  global_secondary_index {
    name               = "priority-due-index"
    hash_key           = "priority_due"
    projection_type    = "ALL"
    write_capacity     = 0
    read_capacity      = 0
  }

  # Point-in-time recovery for data protection
  point_in_time_recovery {
    enabled = true
  }

  # Tags
  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix} Actions Table"
    }
  )
}
