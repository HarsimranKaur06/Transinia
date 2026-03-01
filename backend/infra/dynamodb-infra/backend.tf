terraform {
  backend "s3" {
    bucket         = "transinia-terraform-state"
    # key will be provided during terraform init
    region         = "us-east-1"
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}
