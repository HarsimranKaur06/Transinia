# Task execution role (pull from ECR, write logs)
resource "aws_iam_role" "ecs_task_execution" {
  name               = "${local.app}-${local.env}-ecsTaskExecutionRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json
}

data "aws_iam_policy_document" "ecs_task_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_attach" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Add explicit CloudWatch Logs permissions for the ECS task execution role
resource "aws_iam_role_policy" "ecs_cloudwatch_logs" {
  name = "${local.app}-${local.env}-cloudwatch-logs-policy"
  role = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ],
        Resource = [
          "arn:aws:logs:${var.aws_region}:*:log-group:/ecs/${local.app}-${local.env}-backend:*",
          "arn:aws:logs:${var.aws_region}:*:log-group:/ecs/${local.app}-${local.env}-frontend:*"
        ]
      }
    ]
  })
}

# Task role (app permissions)
resource "aws_iam_role" "ecs_task_role" {
  name               = "${local.app}-${local.env}-ecsTaskRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json
}

# DynamoDB table ARNs by name (existing tables)
data "aws_dynamodb_table" "meetings" {
  name = var.dynamodb_table_meetings
}

data "aws_dynamodb_table" "actions" {
  name = var.dynamodb_table_actions
}

# Least-privilege DynamoDB access
resource "aws_iam_role_policy" "task_ddb_access" {
  name = "${local.app}-${local.env}-ddb-access"
  role = aws_iam_role.ecs_task_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:BatchGetItem",
        "dynamodb:BatchWriteItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:DescribeTable"
      ],
      Resource = [
        data.aws_dynamodb_table.meetings.arn,
        "${data.aws_dynamodb_table.meetings.arn}/index/*",
        data.aws_dynamodb_table.actions.arn,
        "${data.aws_dynamodb_table.actions.arn}/index/*"
      ]
    }]
  })
}

# Least-privilege S3 access
locals {
  s3_raw_bucket_arn      = "arn:aws:s3:::${var.s3_bucket_raw}"
  s3_raw_bucket_objects  = "arn:aws:s3:::${var.s3_bucket_raw}/*"
  s3_proc_bucket_arn     = "arn:aws:s3:::${var.s3_bucket_processed}"
  s3_proc_bucket_objects = "arn:aws:s3:::${var.s3_bucket_processed}/*"
}

resource "aws_iam_role_policy" "task_s3_access" {
  name = "${local.app}-${local.env}-s3-access"
  role = aws_iam_role.ecs_task_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["s3:ListBucket"],
        Resource = [local.s3_raw_bucket_arn, local.s3_proc_bucket_arn]
      },
      {
        Effect   = "Allow",
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
        Resource = [local.s3_raw_bucket_objects, local.s3_proc_bucket_objects]
      }
    ]
  })
}
