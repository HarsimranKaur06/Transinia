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
   python -m src.app
   ```
3. Check the `outputs/` folder for:
   - `minutes.md`
   - `actions.json`

Edit `samples/transcript.txt` with your own notes and run again.

## Usage

### Local Mode
Process a local transcript file:
```bash
python -m src.app
```

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
```

## Project Structure

```
meeting-bot/
├── src/
│   ├── agents/       # LangGraph agents and nodes
│   ├── config/       # Configuration settings
│   ├── models/       # Data models
│   ├── repositories/ # Storage repositories
│   ├── services/     # Service integrations
│   ├── utils/        # Utilities
│   └── app.py        # Main application entry point
├── outputs/          # Local output directory
├── samples/          # Sample transcript files
├── requirements.txt  # Python dependencies
├── .env              # Environment variables (not in repo)
└── Dockerfile        # Docker configuration
```
