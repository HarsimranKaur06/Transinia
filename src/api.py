"""
API Server for Transinia
------------------------
This module provides a FastAPI server to expose the Transinia functionality
as a REST API for the frontend to consume.
"""

import os
import uuid
import tempfile
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.agents.graph import create_graph
from src.config.settings import settings, logger
from src.models.schemas import MeetingState
from src.repositories.storage_repo import StorageRepository

# Create FastAPI app
app = FastAPI(title="Transinia API", 
              description="API for processing meeting transcripts and generating insights",
              version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you'd want to restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create storage repository
storage_repo = StorageRepository()

# Define API models
class TranscriptResponse(BaseModel):
    id: str
    name: str
    date: str
    size: Optional[int] = None
    source: str = "s3"

class InsightRequest(BaseModel):
    transcriptId: str

class ActionItem(BaseModel):
    id: str
    text: str
    owner: Optional[str] = None
    due: Optional[str] = None
    priority: Optional[str] = "Medium"
    completed: bool = False

class InsightResponse(BaseModel):
    id: str
    title: str
    date: str
    summary: str
    actionItems: List[ActionItem]
    keyPoints: List[str]
    participants: List[str]
    duration: Optional[str] = None
    source: str

@app.get("/")
async def root():
    """Root endpoint that returns API information"""
    return {
        "name": "Transinia API",
        "version": "1.0.0",
        "description": "API for processing meeting transcripts and generating insights"
    }

@app.get("/api/transcripts/list")
async def list_transcripts():
    """List all available transcripts"""
    try:
        # Get transcripts from S3
        s3_transcripts = storage_repo.list_s3_transcripts()
        
        # Format the response
        transcripts = []
        
        for key in s3_transcripts:
            # Get file metadata from S3
            metadata = storage_repo.get_s3_object_metadata(key)
            
            # Extract filename from the S3 key
            filename = os.path.basename(key)
            
            # Format the date (use last modified from metadata if available)
            date_str = datetime.now().strftime("%B %d, %Y")
            if metadata and 'LastModified' in metadata:
                date_str = metadata['LastModified'].strftime("%B %d, %Y")
            
            transcript = TranscriptResponse(
                id=key,
                name=filename,
                date=date_str,
                size=metadata.get('ContentLength') if metadata else None,
                source="s3"
            )
            
            transcripts.append(transcript.model_dump())
        
        return {"transcripts": transcripts}
    
    except Exception as e:
        logger.error(f"Error listing transcripts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list transcripts: {str(e)}")

@app.post("/api/transcripts/upload")
async def upload_transcript(file: UploadFile = File(...)):
    """Upload a new transcript file"""
    try:
        # Check file extension
        if not file.filename.lower().endswith(('.txt', '.md', '.docx')):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file format. Only .txt, .md, and .docx files are supported."
            )
        
        # Read file content
        content = await file.read()
        
        # Generate S3 key (use a UUID to avoid conflicts)
        file_uuid = str(uuid.uuid4())
        filename = file.filename
        s3_key = f"transcripts/{file_uuid}_{filename}"
        
        # Save to S3
        if storage_repo.save_file_to_s3(s3_key, content):
            return {
                "success": True,
                "message": "File uploaded successfully",
                "fileId": s3_key
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to upload file to S3")
            
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error uploading transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload transcript: {str(e)}")

@app.post("/api/insights/generate")
async def generate_insights(request: InsightRequest):
    """Generate insights from a transcript"""
    try:
        # Get transcript from S3
        transcript_id = request.transcriptId
        transcript_content = storage_repo.get_transcript_from_s3(transcript_id)
        
        if not transcript_content:
            raise HTTPException(status_code=404, detail=f"Transcript not found: {transcript_id}")
        
        # Extract filename from the S3 key (used as meeting title)
        filename = os.path.basename(transcript_id)
        
        # Create initial state
        state = MeetingState(transcript=transcript_content, source=transcript_id)
        
        # Create and run the processing graph
        graph = create_graph()
        logger.info(f"Processing transcript: {transcript_id}")
        final_state = graph.invoke(state)
        
        # Extract values from final_state
        if hasattr(final_state, 'get'):
            minutes_md = final_state.get("minutes_md", "")
            agenda = final_state.get("agenda", [])
            decisions = final_state.get("decisions", [])
            tasks = final_state.get("tasks", [])
            participants = final_state.get("participants", [])
        else:
            # Handle AddableValuesDict from LangGraph
            minutes_md = getattr(final_state, "minutes_md", "")
            agenda = getattr(final_state, "agenda", [])
            decisions = getattr(final_state, "decisions", [])
            tasks = getattr(final_state, "tasks", [])
            participants = getattr(final_state, "participants", [])
        
        # Generate insight ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        insight_id = f"insight_{timestamp}"
        
        # Store in DynamoDB if enabled
        if settings.use_dynamodb:
            meeting_id = storage_repo.save_meeting_to_dynamodb(final_state)
            if meeting_id:
                insight_id = meeting_id
                logger.info(f"Meeting saved to DynamoDB with ID: {meeting_id}")
        
        # Always save minutes and actions to S3
        s3_minutes_key = f"minutes/{insight_id}.md"
        s3_actions_key = f"actions/{insight_id}.json"
        
        # Save minutes to S3
        if storage_repo.save_minutes_s3(s3_minutes_key, minutes_md):
            logger.info(f"Minutes saved to S3: {s3_minutes_key}")
        else:
            logger.warning(f"Failed to save minutes to S3: {s3_minutes_key}")
        
        # Save actions to S3
        if tasks:
            if not isinstance(tasks[0], dict):
                tasks_dict = [task.model_dump() for task in tasks]
            else:
                tasks_dict = tasks
                
            if storage_repo.save_actions_s3(s3_actions_key, tasks_dict):
                logger.info(f"Actions saved to S3: {s3_actions_key}")
            else:
                logger.warning(f"Failed to save actions to S3: {s3_actions_key}")
        
        # Save a JSON representation of the full insight for easy retrieval
        insight_data = {
            "id": insight_id,
            "title": f"Meeting Notes: {os.path.splitext(filename)[0]}",
            "date": datetime.now().strftime("%B %d, %Y"),
            "summary": minutes_md[:500] if len(minutes_md) > 500 else minutes_md,
            "actionItems": [
                {
                    "id": str(idx),
                    "text": task.get("task") if isinstance(task, dict) else task.task,
                    "assignee": task.get("owner") if isinstance(task, dict) else getattr(task, "owner", None),
                    "completed": False
                } for idx, task in enumerate(tasks) if tasks
            ],
            "keyPoints": agenda + [f"Decision: {d}" for d in decisions],
            "participants": participants,
            "duration": "Unknown",
            "source": transcript_id
        }
        
        # Save the complete insight data to S3
        s3_insight_key = f"insights/{insight_id}.json"
        storage_repo.save_file_to_s3(
            s3_insight_key, 
            json.dumps(insight_data, indent=2).encode('utf-8')
        )
        logger.info(f"Complete insight data saved to S3: {s3_insight_key}")
        
        # Return success response with the insight ID
        return {
            "success": True,
            "message": "Meeting insights generated successfully",
            "insightId": insight_id
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@app.get("/api/insights/{insight_id}")
async def get_insight(insight_id: str):
    """Get meeting insights by ID"""
    try:
        # First try to get the complete insight JSON from S3
        s3_insight_key = f"insights/{insight_id}.json"
        insight_json = storage_repo.get_file_from_s3(s3_insight_key)
        
        if insight_json:
            # Return the pre-formatted insight JSON
            return json.loads(insight_json)
        
        # If not found, try to get from DynamoDB
        meeting = None
        if settings.use_dynamodb:
            meeting = storage_repo.get_meeting_from_dynamodb(insight_id)
        
        # If not found in DynamoDB, try to get from S3 minutes and actions
        if not meeting:
            # Check if minutes exist in S3
            s3_minutes_key = f"minutes/{insight_id}.md"
            minutes_md = storage_repo.get_file_from_s3(s3_minutes_key)
            
            if not minutes_md:
                raise HTTPException(status_code=404, detail=f"Insight not found: {insight_id}")
            
            # Try to get actions from S3
            s3_actions_key = f"actions/{insight_id}.json"
            actions_json = storage_repo.get_file_from_s3(s3_actions_key)
            
            # Create a basic meeting object
            meeting = {
                "meeting_id": insight_id,
                "date": datetime.now().strftime("%B %d, %Y"),
                "minutes_md": minutes_md,
                "tasks": json.loads(actions_json) if actions_json else [],
                "participants": [],
                "agenda": [],
                "decisions": []
            }
        
        # Extract meeting title from the minutes or use a default
        title = "Meeting Summary"
        if meeting.get("minutes_md"):
            lines = meeting["minutes_md"].split("\n")
            for line in lines:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
        
        # Format action items
        action_items = []
        for task in meeting.get("tasks", []):
            action_item = ActionItem(
                id=str(uuid.uuid4()),
                text=task.get("task", ""),
                owner=task.get("owner"),
                due=task.get("due"),
                priority=task.get("priority", "Medium"),
                completed=task.get("completed", False)
            )
            action_items.append(action_item.model_dump())
        
        # Format key points (use agenda items and decisions)
        key_points = []
        for item in meeting.get("agenda", []):
            key_points.append(item)
        
        for decision in meeting.get("decisions", []):
            key_points.append(f"Decision: {decision}")
        
        # Create response object
        insight = {
            "id": meeting.get("meeting_id", insight_id),
            "title": title,
            "date": meeting.get("date", datetime.now().strftime("%B %d, %Y")),
            "summary": meeting.get("summary", meeting.get("minutes_md", "")[:500]),
            "actionItems": action_items,
            "keyPoints": key_points,
            "participants": meeting.get("participants", []),
            "duration": meeting.get("duration", "Unknown"),
            "source": meeting.get("source", "Unknown")
        }
        
        # Save this formatted insight for future use
        storage_repo.save_file_to_s3(
            s3_insight_key, 
            json.dumps(insight, indent=2).encode('utf-8')
        )
        logger.info(f"Created and saved formatted insight to S3: {s3_insight_key}")
        
        return insight
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting insight: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get insight: {str(e)}")

# Add missing import at the top of the file
import json

def run_api(port=5000):
    """Run the FastAPI server using uvicorn"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    run_api()
