# How to Use DynamoDB with Transinia

Now that you've deployed the DynamoDB tables, you can start using them with your Transinia application. Here's a step-by-step guide on how to use DynamoDB for meeting data storage and retrieval.

## 1. Update Your .env File

First, make sure your `.env` file has the correct DynamoDB settings:

```
# DynamoDB Configuration
USE_DYNAMODB=true
DYNAMODB_TABLE_MEETINGS=transinia-meetings
DYNAMODB_TABLE_ACTIONS=transinia-actions
```

## 2. Process a Meeting Transcript

Run the application to process a meeting transcript. The data will automatically be stored in DynamoDB:

```powershell
python src/app.py --file samples/transcript.txt
```

The application will:
1. Process the transcript
2. Extract agenda items, decisions, and tasks
3. Store the data locally
4. If DynamoDB is enabled, also store it in DynamoDB

## 3. Query Meeting Data

You can use the new command-line arguments to query data from DynamoDB:

### List Meetings by Participant

```powershell
python src/app.py --list-participants --participant "Alice Smith"
```

This will show all meetings where Alice Smith was a participant.

### List Tasks for a Person

```powershell
python src/app.py --list-tasks --owner "Bob Johnson"
```

This will show all tasks assigned to Bob Johnson across all meetings.

### List High Priority Tasks

```powershell
python src/app.py --high-priority
```

This will show all high priority tasks across all meetings.

## 4. Use the DynamoDB Service in Your Code

You can also use the DynamoDB service directly in your code:

```python
from src.services.dynamodb_service import DynamoDBService

# Create service instance
db_service = DynamoDBService()

# Store a meeting
meeting_id = db_service.store_meeting(meeting_state)

# Get a meeting
meeting = db_service.get_meeting(meeting_id)

# Find meetings by participant
meetings = db_service.find_meetings_by_participant("Alice Smith")

# Find tasks by owner
tasks = db_service.find_tasks_by_owner("Bob Johnson")

# Find high priority tasks
high_priority = db_service.find_high_priority_tasks()

# Mark a task as completed
db_service.mark_task_completed(action_id, meeting_id, completed=True)
```

## 5. Try the Example Scripts

For a quick demonstration, try running the example scripts:

```powershell
python scripts/dynamodb_examples.py
```

This script creates a sample meeting, stores it in DynamoDB, and demonstrates various queries.

## 6. Extend with Custom Queries

You can add new query capabilities as needed. The `scripts/add_due_date_query.py` script shows how to add a new method to find tasks by due date:

```powershell
python scripts/add_due_date_query.py
```

## 7. When You're Done

When you're finished using DynamoDB, you can destroy the tables to avoid ongoing costs:

```powershell
cd infra/terraform
.\Deploy-DynamoDB.ps1 destroy
```

This will remove the DynamoDB tables while preserving your local data.

## Troubleshooting

- If you get authentication errors, check your AWS credentials in `.env`
- If tables aren't found, make sure the table names in `.env` match what you created with Terraform
- If you see "attribute not found" errors, you may need to update your data structure to match the schema

Happy analyzing!
