# Terraform Workflow Commands

## 1. Initialize Backend (per module)

- grafana-infra:
  terraform init -backend-config="key=grafana-infra/dev/terraform.tfstate"

- ecs-fargate-infra:
  terraform init -backend-config="key=ecs-fargate-infra/dev/terraform.tfstate"

- s3-bucket-infra:
  terraform init -backend-config="key=s3-bucket-infra/dev/terraform.tfstate"

- dynamodb-infra:
  terraform init -backend-config="key=dynamodb-infra/dev/terraform.tfstate"

## 2. Create Workspace (if not already created)
terraform workspace new dev

## 3. Select Workspace
terraform workspace select dev

## 4. Plan
terraform plan -out=dev.plan

## 5. Apply
terraform apply dev.plan

#
# ---
#
## Production Workspace Example

1. Initialize Backend (per module)

- grafana-infra:
  terraform init -backend-config="key=grafana-infra/prod/terraform.tfstate"

- ecs-fargate-infra:
  terraform init -backend-config="key=ecs-fargate-infra/prod/terraform.tfstate"

- s3-bucket-infra:
  terraform init -backend-config="key=s3-bucket-infra/prod/terraform.tfstate"

- dynamodb-infra:
  terraform init -backend-config="key=dynamodb-infra/prod/terraform.tfstate"

2. Create Workspace (if not already created)
terraform workspace new prod

3. Select Workspace
terraform workspace select prod

4. Plan
terraform plan -out=prod.plan

5. Apply
terraform apply prod.plan
