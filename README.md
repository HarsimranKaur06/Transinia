````markdown
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
   pip install -r requirements.txt
   cp .env.example .env
   # Open .env and paste your OpenAI key and AWS credentials if using S3
   python -m src.app
   ```
3. Check the `outputs/` folder for:
   - `minutes.md`
   - `actions.json`

Edit `samples/transcript.txt` with your own notes and run again.

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

````
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
   pip install -r requirements.txt
   cp .env.example .env
   # Open .env and paste your OpenAI key and AWS credentials if using S3
   python -m src.app
   ```
3. Check the `outputs/` folder for:
   - `minutes.md`
   - `actions.json`

Edit `samples/transcript.txt` with your own notes and run again.

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
