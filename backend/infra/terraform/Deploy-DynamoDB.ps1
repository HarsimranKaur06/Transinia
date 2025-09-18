# Script to create or destroy DynamoDB tables using Terraform and .env values

# Script location and file paths
$ScriptDir = $PSScriptRoot
$EnvFile = Join-Path (Split-Path (Split-Path $ScriptDir -Parent) -Parent) ".env"
$TerraformDir = $ScriptDir

# Function to read .env file and extract a value
function Get-EnvValue {
    param (
        [string]$Key
    )
    
    $value = Get-Content $EnvFile | Where-Object { $_ -match "^$Key=" } | ForEach-Object { $_ -replace "^$Key=", "" }
    return $value
}

# Check if .env file exists
if (-not (Test-Path $EnvFile)) {
    Write-Error "Error: .env file not found at $EnvFile"
    exit 1
}

# Read values from .env
$AWS_ACCESS_KEY_ID = Get-EnvValue -Key "AWS_ACCESS_KEY_ID"
$AWS_SECRET_ACCESS_KEY = Get-EnvValue -Key "AWS_SECRET_ACCESS_KEY"
$AWS_REGION = Get-EnvValue -Key "AWS_REGION"
$DYNAMODB_TABLE_MEETINGS = Get-EnvValue -Key "DYNAMODB_TABLE_MEETINGS"
$DYNAMODB_TABLE_ACTIONS = Get-EnvValue -Key "DYNAMODB_TABLE_ACTIONS"

# Check if required values are present
if ([string]::IsNullOrEmpty($AWS_ACCESS_KEY_ID) -or [string]::IsNullOrEmpty($AWS_SECRET_ACCESS_KEY) -or [string]::IsNullOrEmpty($AWS_REGION)) {
    Write-Error "Error: AWS credentials or region missing in .env file"
    exit 1
}

if ([string]::IsNullOrEmpty($DYNAMODB_TABLE_MEETINGS) -or [string]::IsNullOrEmpty($DYNAMODB_TABLE_ACTIONS)) {
    Write-Warning "Warning: DynamoDB table names missing in .env file, using defaults"
    $DYNAMODB_TABLE_MEETINGS = "meeting-bot-meetings"
    $DYNAMODB_TABLE_ACTIONS = "meeting-bot-actions"
}

# Create terraform.tfvars file
$TfvarsContent = @"
aws_region = "$AWS_REGION"
aws_access_key_id = "$AWS_ACCESS_KEY_ID"
aws_secret_access_key = "$AWS_SECRET_ACCESS_KEY"
dynamodb_table_meetings = "$DYNAMODB_TABLE_MEETINGS"
dynamodb_table_actions = "$DYNAMODB_TABLE_ACTIONS"
environment = "dev"
project = "Transinia"
"@

$TfvarsFile = Join-Path $TerraformDir "terraform.tfvars"
Set-Content -Path $TfvarsFile -Value $TfvarsContent

# Change to Terraform directory
Set-Location $TerraformDir

# Parse command line arguments
$Action = if ($args.Count -gt 0) { $args[0] } else { "apply" }

if ($Action -eq "apply" -or $Action -eq "create") {
    Write-Host "Creating DynamoDB tables..."
    terraform init
    terraform apply -auto-approve
    Write-Host "DynamoDB tables created successfully!" -ForegroundColor Green
}
elseif ($Action -eq "destroy" -or $Action -eq "delete") {
    Write-Host "Destroying DynamoDB tables..." -ForegroundColor Yellow
    terraform init
    terraform destroy -auto-approve
    Write-Host "DynamoDB tables destroyed successfully!" -ForegroundColor Green
}
else {
    Write-Error "Invalid action. Use 'apply'/'create' or 'destroy'/'delete'"
    exit 1
}

# Clean up sensitive information
Remove-Item -Path $TfvarsFile -Force

Write-Host "Done!" -ForegroundColor Green
