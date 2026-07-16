//Added for setting up prometheus monitoring
terraform {
  backend "s3" {
    bucket         = "transinia-terraform-state"
    key            = "prometheus-infra/dev/terraform.tfstate"
    region         = "us-east-1" // Change to your region
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}
