# Transinia Utility Scripts

This directory contains standalone scripts for common operations with the Transinia application, especially for querying DynamoDB.

## Available Scripts

### High Priority Tasks

```
python -m scripts.high_priority_tasks
```

Lists all high priority tasks stored in DynamoDB.

### Find Meetings by Participant

```
python -m scripts.find_meetings_by_participant "John Doe"
```

Finds all meetings that include the specified participant.

### Find Tasks by Owner

```
python -m scripts.find_tasks_by_owner "Jane Smith"
```

Finds all tasks assigned to the specified owner.

### Get Meeting

```
python -m scripts.get_meeting "meeting_20240101123456"
```

Retrieves a specific meeting by its ID and displays its details.

### List S3 Transcripts

```
python -m scripts.list_s3_transcripts
```

Lists all available transcripts stored in the S3 bucket.

## Using the Main Application

To avoid naming conflicts with Python packages, use the `run_transinia.py` script in the root directory:

```
python run_transinia.py
```

All command line arguments work as normal:

```
python run_transinia.py --high-priority
python run_transinia.py --list-participants --participant "John Doe"
```
