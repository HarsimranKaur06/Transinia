resource "aws_s3_bucket" "terraform_state" {
  bucket = "transinia-terraform-state"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Name = "Terraform State Bucket"
    Environment = "shared"
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-state-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
  tags = {
    Name = "Terraform State Lock Table"
    Environment = "shared"
  }
}
