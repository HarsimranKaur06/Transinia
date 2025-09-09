# Smart Meeting Minutes

This app turns a plain-text meeting transcript into neat **Minutes (Markdown)** and **Action Items (JSON)** using **LangGraph + OpenAI**. It supports both local files and S3 storage.

## Features

- Process transcripts from local files or S3 buckets
- Generate well-formatted meeting minutes
- Extract actionable tasks with assignees, due dates, and priorities
- Save outputs locally or to S3

## Quick Start
1. Install Python 3.13+
2. In a terminal:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Open .env and paste your OpenAI key and AWS credentials if using S3
   python run_app.py
   ```
3. Check the `outputs/` folder for:
   - `minutes.md`
   - `actions.json`

Edit `samples/transcript.txt` with your own notes and run again.

## Usage

### Local Mode
Process a local transcript file:
```bash
python run_app.py
```

### S3 Mode
List available transcripts in S3:
```bash
python run_app.py --list-s3
```

Process a transcript from S3:
```bash
python run_app.py --source s3 --s3-key transcript.txt
```

## Docker

### Build the Docker image
```bash
docker build -t meeting-bot .
```

### Run the Docker container
```bash
# Local mode
docker run --env-file .env meeting-bot

# S3 mode
docker run --env-file .env meeting-bot --source s3 --s3-key transcript.txt

# List S3 transcripts
docker run --env-file .env meeting-bot --list-s3

# Query DynamoDB for high-priority tasks
docker run --env-file .env meeting-bot --high-priority

# Find meetings by participant
docker run --env-file .env meeting-bot --list-participants --participant "John Doe"
```

## Project Structure

```
transinia/
├── docs/             # Documentation
├── src/
│   ├── agents/       # LangGraph agents and nodes
│   ├── config/       # Configuration settings
│   ├── models/       # Data models
│   ├── repositories/ # Storage repositories
│   ├── scripts/      # Standalone scripts for specific operations
│   ├── services/     # Service integrations
│   ├── utils/        # Utilities
│   └── app.py        # Main application code
├── outputs/          # Local output directory
├── samples/          # Sample transcript files
├── requirements.txt  # Python dependencies
├── run_app.py        # Wrapper script
├── .env              # Environment variables (not in repo)
└── Dockerfile        # Docker configuration
```

## DynamoDB Integration

To use DynamoDB for persistent storage:

1. Set the following environment variables in your `.env` file:
   ```
   USE_DYNAMODB=true
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=your_region
   DYNAMODB_MEETINGS_TABLE=Meetings
   DYNAMODB_TASKS_TABLE=Tasks
   ```

2. Query high priority tasks:
   ```bash
   python run_app.py --high-priority
   
   # Alternatively, use the dedicated script
   python -m src.scripts.high_priority_tasks
   ```

3. Find meetings by participant:
   ```bash
   python run_app.py --list-participants --participant "John Doe"
   
   # Alternatively, use the dedicated script
   python -m src.scripts.find_meetings_by_participant "John Doe"
   ```

4. Find tasks by owner:
   ```bash
   python run_app.py --list-tasks --owner "Jane Smith"
   
   # Alternatively, use the dedicated script
   python -m src.scripts.find_tasks_by_owner "Jane Smith"
   ```

The `src/scripts/` directory contains standalone scripts for specific operations, which can be useful for automation or integration with other tools.
