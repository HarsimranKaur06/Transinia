# Smart Meeting Minutes (Transinia)

This app turns a plain-text meeting transcript into neat **Minutes (Markdown)** and **Action Items (JSON)** using **LangGraph + OpenAI**. It supports both local files and S3 storage.

## Features

- Process transcripts from local files or S3 buckets
- Generate well-formatted meeting minutes
- Extract actionable tasks with assignees, due dates, and priorities
- Save outputs locally or to S3
- Web-based frontend for transcript management and insight viewing
- API server for frontend integration

## Quick Start
1. Install Python 3.13+
2. In a terminal:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   
   # Copy and configure environment variables
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your API keys and AWS credentials
   
   python backend/run_app.py
   ```
3. Check the `backend/outputs/` folder for:
   - `minutes.md`
   - `actions.json`

## Docker Setup

### Prerequisites

#### 1. Install Docker and Docker Compose
Make sure Docker Desktop is installed and running.

#### 2. Set Up AWS Infrastructure
Before running the application, you need to create the required AWS resources. You have two options:

**Option A: Use Terraform (Recommended)**
```bash
# Create S3 buckets
cd backend/infra/s3-bucket-infra
terraform init
terraform apply -var-file="dev.tfvars"

# Create DynamoDB tables
cd ../dynamodb-infra
terraform init
terraform apply -var-file="dev.tfvars"
```
This will create:
- S3 buckets: `transinia-dev-transcripts` and `transinia-dev-outputs`
- DynamoDB tables: `transinia-dev-meetings` and `transinia-dev-actions`

**Option B: Create Manually**
- Create 2 S3 buckets in your AWS account
- Create 2 DynamoDB tables with appropriate schemas (see `docs/DYNAMODB.md`)

#### 3. Configure Environment Variables
```bash
# Copy the example environment file
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your credentials:
- `OPENAI_API_KEY` - Your OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `AWS_REGION` - Your AWS region (e.g., `us-east-1`)
- `S3_BUCKET_RAW` - Your S3 bucket for raw transcripts
- `S3_BUCKET_PROCESSED` - Your S3 bucket for processed outputs
- `DYNAMODB_TABLE_MEETINGS` - Your DynamoDB meetings table name
- `DYNAMODB_TABLE_ACTIONS` - Your DynamoDB actions table name

### Run with Docker Compose
```bash
# Start both backend and frontend
docker-compose up --build

# Access the application:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8001
# - Health check: http://localhost:8001/health
```

### Run Individual Containers
Backend only:
```bash
docker build -t transinia-backend ./backend
docker run --env-file backend/.env -p 8001:8001 transinia-backend
```

Frontend only:
```bash
docker build -t transinia-frontend ./frontend --build-arg NEXT_PUBLIC_BACKEND_URL=http://localhost:8001
docker run -p 3000:3000 transinia-frontend
```

## Usage

### CLI Mode
Process a local transcript file:
```bash
python -m src.app
```

### API Server Mode
Start the API server for frontend integration:
```bash
python run_api.py
```
This will start a FastAPI server at http://localhost:5000.

### Frontend
The project includes a Next.js frontend in the `frontend/` directory.

To run the frontend:
```bash
cd frontend
npm install
npm run dev
```

This will start the frontend development server, typically at http://localhost:3000.

## Frontend-Backend Integration

The frontend and backend are designed to work together:

1. The backend (FastAPI) provides API endpoints at http://localhost:5000:
   - `/api/transcripts/list` - List available transcripts
   - `/api/transcripts/upload` - Upload a new transcript
   - `/api/insights/generate` - Generate insights from a transcript
   - `/api/insights/{insight_id}` - Get meeting insights by ID

2. The frontend connects to these endpoints through the API client in `frontend/src/lib/api/index.js`.

3. To connect the frontend to the backend:
   - Start the backend: `python run_api.py`
   - Start the frontend: `cd frontend && npm run dev`
   - Make sure your `.env.local` file in the frontend directory has the correct API URLs:
     ```
     NEXT_PUBLIC_API_URL=http://localhost:3000/api
     NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
     ```

4. The frontend will fetch data from:
   - Transcripts from the S3 bucket "meeting-bot-transcripts"
   - Processed insights from the S3 bucket "meeting-bot-outputs"

### S3 Mode
List available transcripts in S3:
```bash
python -m src.app --list-s3
```

Process a transcript from S3:
```bash
python -m src.app --source s3 --s3-key transcript.txt
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
├── frontend/         # Next.js frontend application
├── src/
│   ├── agents/       # LangGraph agents and nodes
│   ├── config/       # Configuration settings
│   ├── models/       # Data models
│   ├── repositories/ # Storage repositories
│   ├── scripts/      # Standalone scripts for specific operations
│   ├── services/     # Service integrations
│   ├── utils/        # Utilities
│   ├── app.py        # Main application code
│   └── api.py        # FastAPI server for frontend integration
├── outputs/          # Local output directory
├── samples/          # Sample transcript files
├── requirements.txt  # Python dependencies
├── run_api.py        # API server script
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
   python -m src.app --high-priority
   
   # Alternatively, use the dedicated script
   python -m src.scripts.high_priority_tasks
   ```

3. Find meetings by participant:
   ```bash
   python -m src.app --list-participants --participant "John Doe"
   
   # Alternatively, use the dedicated script
   python -m src.scripts.find_meetings_by_participant "John Doe"
   ```

4. Find tasks by owner:
   ```bash
   python -m src.app --list-tasks --owner "Jane Smith"
   
   # Alternatively, use the dedicated script
   python -m src.scripts.find_tasks_by_owner "Jane Smith"
   ```

The `src/scripts/` directory contains standalone scripts for specific operations, which can be useful for automation or integration with other tools.

## Monitoring

### Error Tracking & Performance Monitoring (Sentry)
The application integrates with Sentry for real-time error tracking and performance monitoring:

- **Error Tracking:** Captures Python exceptions with stack traces
- **Performance Monitoring:** Tracks API response times and slow queries
- **Security:** Automatically filters sensitive data (AWS keys, API keys)
- **Environments:** Separate monitoring for dev and prod

**Setup:**
1. Configure `DEV_SENTRY_DSN` and `PROD_SENTRY_DSN` in GitHub Secrets
2. Deploy application (Sentry initializes automatically)
3. View errors and performance at: https://sentry.io/

### CloudWatch Logs
Application logs are available in AWS CloudWatch:
- Dev Backend: `/ecs/transinia-dev-backend`
- Dev Frontend: `/ecs/transinia-dev-frontend`
- Prod Backend: `/ecs/transinia-prod-backend`
- Prod Frontend: `/ecs/transinia-prod-frontend`

