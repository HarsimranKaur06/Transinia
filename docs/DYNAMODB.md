# DynamoDB Integration Guide

## Overview

This guide covers setting up and using DynamoDB with Transinia. DynamoDB provides a scalable, high-performance NoSQL database for storing meeting records and action items.

## Table Structure

Transinia uses two DynamoDB tables:

### 1. Meetings Table
- **Primary key:** `meeting_id` (String)
- **Sort key:** `date` (String)
- **Global Secondary Indexes:**
  - `participant-index` - For finding meetings by participant
  - `due-date-index` - For finding meetings by due date

### 2. Actions Table
- **Primary key:** `action_id` (String)
- **Sort key:** `meeting_id` (String)
- **Global Secondary Indexes:**
  - `owner-index` - For finding tasks by assignee
  - `priority-due-index` - For finding tasks by priority and due date

## Setup

### Prerequisites

- AWS account with appropriate permissions
- AWS CLI installed and configured
- Terraform installed (version 0.13+)

### Environment Configuration

Update your `.env` file with DynamoDB settings:

```
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region

# DynamoDB Configuration
USE_DYNAMODB=true
DYNAMODB_TABLE_MEETINGS=transinia-meetings
DYNAMODB_TABLE_ACTIONS=transinia-actions
```

### Deploy Tables with Terraform

1. Navigate to the infrastructure directory:
   ```powershell
   cd backend/infra/dynamodb-infra
   ```

2. Deploy the tables:

   **Windows:**
   ```powershell
   .\Deploy-DynamoDB.ps1
   ```

   **Linux/macOS:**
   ```bash
   ./deploy_dynamodb.sh
   ```

3. To destroy tables when done:
   ```powershell
   .\Deploy-DynamoDB.ps1 destroy
   ```

## Usage

### Process Meeting Transcripts

The application automatically stores data in DynamoDB when enabled:

```powershell
python src/app.py --file samples/transcript.txt
```

The application will:
1. Process the transcript
2. Extract agenda items, decisions, and tasks
3. Store data locally
4. Store in DynamoDB (if enabled)

### Query Meeting Data

#### List Meetings by Participant

```powershell
python src/app.py --list-participants --participant "Alice Smith"
```

#### List Tasks by Owner

```powershell
python src/app.py --list-tasks --owner "Bob Johnson"
```

#### List High Priority Tasks

```powershell
python src/app.py --high-priority
```

### Using DynamoDB Service in Code

```python
from src.services.dynamodb_service import DynamoDBService

# Initialize service
db_service = DynamoDBService()

# Store a meeting
meeting_id = db_service.store_meeting(meeting_state)

# Retrieve a meeting
meeting = db_service.get_meeting(meeting_id)

# Find meetings by participant
meetings = db_service.find_meetings_by_participant("Alice Smith")

# Find tasks by owner
tasks = db_service.find_tasks_by_owner("Bob Johnson")

# Find high priority tasks
high_priority = db_service.find_high_priority_tasks()

# Mark task as completed
db_service.mark_task_completed(action_id, meeting_id, completed=True)
```

## Key Components

### DynamoDBService
Location: `src/services/dynamodb_service.py`

**Methods:**
- `store_meeting(state)` - Store meeting in DynamoDB
- `get_meeting(meeting_id)` - Retrieve meeting by ID
- `find_meetings_by_participant(name)` - Find meetings by participant
- `find_tasks_by_owner(owner)` - Find tasks by assignee
- `find_high_priority_tasks()` - Find all high priority tasks
- `mark_task_completed(action_id, meeting_id, completed)` - Mark task completion

### StorageRepository
Location: `src/repositories/storage_repo.py`

Provides unified interface for storage operations, delegating to DynamoDBService when DynamoDB is enabled.

## Example Scripts

### Basic Examples
```powershell
python scripts/dynamodb_examples.py
```

Demonstrates:
- Creating sample meetings
- Storing in DynamoDB
- Various query operations

### Extending Functionality
```powershell
python scripts/add_due_date_query.py
```

Example of adding custom query capabilities.

## Cost Considerations

- **Billing Mode:** On-demand (pay-per-request)
- **Point-in-Time Recovery:** Optional, increases costs
- **Global Secondary Indexes:** Increase storage and operation costs

## Troubleshooting

### Authentication Errors
- Verify AWS credentials in `.env` file
- Check IAM user has DynamoDB permissions

### Table Not Found
- Confirm tables created with deployment script
- Verify table names match `.env` configuration

### Cannot Write to Table
- Check IAM user has write permissions
- Verify tables are in active state

### Attribute Not Found Errors
- Update data structure to match schema
- Check field names in meeting state

## Additional Resources

- See `backend/infra/dynamodb-infra/` for Terraform configurations
- See `backend/scripts/` for more query examples
- DynamoDB documentation: https://docs.aws.amazon.com/dynamodb/
