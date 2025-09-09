# Documentation for using DynamoDB with Transinia

## Overview

This document provides instructions for setting up and using DynamoDB with Transinia. DynamoDB provides a scalable, high-performance NoSQL database for storing meeting records and action items.

## Table Structure

Transinia uses two DynamoDB tables:

1. **Meetings Table** - Stores complete meeting records
   - Primary key: `meeting_id` (String)
   - Sort key: `date` (String)
   - Global Secondary Indexes:
     - `participant-index` - For finding meetings by participant
     - `due-date-index` - For finding meetings by due date

2. **Actions Table** - Stores individual action items for easier querying
   - Primary key: `action_id` (String)
   - Sort key: `meeting_id` (String)
   - Global Secondary Indexes:
     - `owner-index` - For finding tasks by assignee
     - `priority-due-index` - For finding tasks by priority and due date

## Setup Instructions

### Prerequisites

1. AWS account with appropriate permissions
2. AWS CLI installed and configured
3. Terraform installed (version 0.13+)
4. .env file with AWS credentials and table names

### Environment Variables

Create or update your `.env` file with the following variables:

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
DYNAMODB_TABLE_MEETINGS=your_meetings_table_name
DYNAMODB_TABLE_ACTIONS=your_actions_table_name
USE_DYNAMODB=True
```

### Deploying the Tables

1. Navigate to the `infra/terraform` directory
2. Run the deployment script:

   **Windows (PowerShell):**
   ```powershell
   .\Deploy-DynamoDB.ps1
   ```

   **Linux/macOS (Bash):**
   ```bash
   ./deploy_dynamodb.sh
   ```

3. To destroy the tables, run the same script with "destroy" parameter:

   **Windows (PowerShell):**
   ```powershell
   .\Deploy-DynamoDB.ps1 destroy
   ```

   **Linux/macOS (Bash):**
   ```bash
   ./deploy_dynamodb.sh destroy
   ```

## Using DynamoDB in the Application

### Enabling DynamoDB

In your `.env` file, set:

```
USE_DYNAMODB=True
```

### Key Classes and Methods

1. **DynamoDBService** (`src/services/dynamodb_service.py`)
   - `store_meeting(state)` - Stores a meeting in DynamoDB
   - `get_meeting(meeting_id)` - Retrieves a meeting by ID
   - `find_meetings_by_participant(name)` - Finds meetings by participant
   - `find_tasks_by_owner(owner)` - Finds tasks by assignee
   - `find_high_priority_tasks()` - Finds all high priority tasks
   - `mark_task_completed(action_id, meeting_id, completed)` - Marks a task as completed

2. **StorageRepository** (`src/repositories/storage_repo.py`)
   - Provides a unified interface for storage operations
   - Delegates to DynamoDBService when DynamoDB is enabled

### Example Usage

See `scripts/dynamodb_examples.py` for complete examples of using DynamoDB.

Basic usage:

```python
from src.services.dynamodb_service import DynamoDBService

# Create a DynamoDB service instance
dynamodb = DynamoDBService()

# Store a meeting
meeting_id = dynamodb.store_meeting(meeting_state)

# Find all tasks for a specific person
tasks = dynamodb.find_tasks_by_owner("Alice Smith")

# Find high priority tasks
high_priority_tasks = dynamodb.find_high_priority_tasks()
```

## Extending DynamoDB Functionality

See `scripts/add_due_date_query.py` for an example of adding new query capabilities.

## Cost Considerations

- DynamoDB uses on-demand (pay-per-request) billing mode
- Enabling point-in-time recovery increases costs
- Global Secondary Indexes increase storage and operation costs

## Troubleshooting

Common issues:

1. **Authentication Errors**
   - Check your AWS credentials in the `.env` file
   - Verify that your IAM user has permissions for DynamoDB

2. **Table Not Found**
   - Verify that the tables have been created with the deployment script
   - Check the table names in your `.env` file

3. **Cannot Write to Table**
   - Check that your IAM user has write permissions
   - Verify that the tables are in an active state
