# Transinia Backend

FastAPI service exposing transcript ingestion, processing, and insights. Includes a CLI pipeline and optional S3/DynamoDB integrations.

## Run (virtualenv)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m backend.src.app            # CLI
python run_api.py                    # API server on port 5000
# or: python -m uvicorn backend.src.api:app --host 0.0.0.0 --port 5000
```

## API Endpoints (default base http://localhost:5000)
- `GET  /api/transcripts/list`
- `POST /api/transcripts/upload`
- `POST /api/insights/generate`
- `GET  /api/insights/{insight_id}`

## S3 Mode
```bash
python -m backend.src.app --list-s3
python -m backend.src.app --source s3 --s3-key transcript.txt
```

## DynamoDB Integration
Set in `.env`:
```
USE_DYNAMODB=true
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
DYNAMODB_MEETINGS_TABLE=Meetings
DYNAMODB_TASKS_TABLE=Tasks
```
Queries:
```bash
python -m backend.src.app --high-priority
python -m backend.src.app --list-participants --participant "John Doe"
python -m backend.src.app --list-tasks --owner "Jane Smith"
# or dedicated scripts if present:
python -m backend.src.scripts.high_priority_tasks
python -m backend.src.scripts.find_meetings_by_participant "John Doe"
python -m backend.src.scripts.find_tasks_by_owner "Jane Smith"
```

## Docker

```bash
docker build -t meeting-bot .
docker run --env-file .env -p 5000:5000 meeting-bot
```

## Project Structure
```
backend/
  Dockerfile
  requirements.txt
  run_api.py
  src/
    api.py
    app.py
    agents/
    services/
    repositories/
    config/
    models/
    scripts/
    utils/
```