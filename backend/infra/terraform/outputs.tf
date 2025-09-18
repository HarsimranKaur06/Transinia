# outputs.tf - Output values for Transinia DynamoDB resources

output "meetings_table_name" {
  description = "Name of the DynamoDB meetings table"
  value       = aws_dynamodb_table.meetings.name
}

output "meetings_table_arn" {
  description = "ARN of the DynamoDB meetings table"
  value       = aws_dynamodb_table.meetings.arn
}

output "actions_table_name" {
  description = "Name of the DynamoDB actions table"
  value       = aws_dynamodb_table.actions.name
}

output "actions_table_arn" {
  description = "ARN of the DynamoDB actions table"
  value       = aws_dynamodb_table.actions.arn
}

output "region" {
  description = "AWS region where resources were created"
  value       = var.aws_region
}
