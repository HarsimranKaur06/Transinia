"""
API Server for Transinia
------------------------
This module provides a FastAPI server to expose the Transinia functionality
as a REST API for the frontend to consume.
"""

import uuid
import json
import os
import tempfile
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.src.agents.graph import create_graph
from backend.src.config.settings import settings, logger
from backend.src.models.schemas import MeetingState
from backend.src.repositories.storage_repo import StorageRepository


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

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for ECS container health checks"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Define API models
class TranscriptResponse(BaseModel):
    id: str
    name: str
    date: str
    size: Optional[int] = None
    source: str = "s3"
    processed: bool = False
    meetingDataId: Optional[str] = None

class MeetingDataRequest(BaseModel):
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
        # Debug: print AWS credentials (redacted)
        logger.info(f"AWS Access Key ID available: {'Yes' if settings.aws_access_key_id else 'No'}")
        logger.info(f"AWS Secret Key available: {'Yes' if settings.aws_secret_access_key else 'No'}")
        logger.info(f"S3 Bucket Raw: {settings.s3_bucket_raw}")
        
        # Get transcripts from S3
        s3_transcripts = storage_repo.list_s3_transcripts()
        logger.info(f"S3 transcripts found: {len(s3_transcripts)}")
        
        # Get all meeting data files to check which transcripts have been processed
        s3_meeting_data = storage_repo.list_processed_files("meeting_data/")
        meeting_data_entries = []
        
        # Load all meeting data entries to match with transcripts
        for key in s3_meeting_data:
            if key.endswith(".json"):
                meeting_data_json = storage_repo.get_file_from_s3(key)
                if meeting_data_json:
                    try:
                        meeting_data = json.loads(meeting_data_json)
                        if "source" in meeting_data and "id" in meeting_data:
                            meeting_data_entries.append({
                                "source": meeting_data["source"],
                                "id": meeting_data["id"]
                            })
                    except json.JSONDecodeError:
                        logger.warning(f"Could not parse meeting data JSON: {key}")
        
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
            
            # Check if this transcript has been processed
            processed = False
            meeting_data_id = None
            
            for entry in meeting_data_entries:
                if entry["source"] == key:
                    processed = True
                    meeting_data_id = entry["id"]
                    break
            
            transcript = TranscriptResponse(
                id=key,
                name=filename,
                date=date_str,
                size=metadata.get('ContentLength') if metadata else None,
                source="s3",
                processed=processed,
                meetingDataId=meeting_data_id
            )
            
            transcripts.append(transcript.model_dump())
        
        return {"transcripts": transcripts}
    
    except Exception as e:
        logger.error(f"Error listing transcripts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list transcripts: {str(e)}")

@app.get("/api/transcripts/{transcript_id}")
async def get_transcript(transcript_id: str):
    """Get the content of a transcript by ID"""
    try:
        # Log the incoming transcript ID
        logger.info(f"API Endpoint: Getting transcript with ID: {transcript_id}")
        
        # Clean up the transcript ID - remove any URL encoding
        import urllib.parse
        decoded_id = urllib.parse.unquote(transcript_id)
        logger.info(f"Decoded transcript ID: {decoded_id}")
        
        # Check if this looks like a UUID
        import re
        uuid_pattern = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
        uuid_match = re.search(uuid_pattern, decoded_id)
        
        # If we have a UUID in the transcript ID, log it
        if uuid_match:
            uuid = uuid_match.group(1)
            logger.info(f"Transcript ID contains UUID: {uuid}")
            
            # First try with the UUID only if the ID is exactly a UUID
            if decoded_id == uuid:
                logger.info(f"ID is exactly a UUID, trying various formats with UUID: {uuid}")
                # Just let the S3 service handle it - it has specialized UUID search
        
        # Try to get the transcript - the S3 service now has robust handling of various key formats
        transcript_content = storage_repo.get_transcript_from_s3(decoded_id)
        
        # Log the result of the retrieval attempt
        logger.info(f"Transcript retrieval result: {'Success' if transcript_content else 'Not Found'}")
        
        if not transcript_content:
            # Get list of all transcripts to log what's available
            all_transcripts = storage_repo.list_s3_transcripts()
            logger.info(f"Available transcripts: {all_transcripts}")
            
            logger.error(f"Transcript not found after all attempts: {transcript_id}")
            raise HTTPException(status_code=404, detail=f"Transcript not found: {transcript_id}")
        
        # Extract filename from the S3 key - get the basename without path
        filename = os.path.basename(decoded_id)
        
        # Return the transcript content with the filename
        return {
            "success": True,
            "filename": filename,
            "content": transcript_content
        }
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get transcript: {str(e)}")
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get transcript: {str(e)}")

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
        
        # Save to S3 - we'll force this to go to the raw bucket
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

@app.post("/api/meeting-data/generate")
async def generate_meeting_data(request: MeetingDataRequest):
    """Generate meeting data from a transcript"""
    try:
        # Get transcript from S3
        transcript_id = request.transcriptId
        
        # First, check if this transcript has already been processed
        # Get all meeting data files to check
        s3_meeting_data = storage_repo.list_processed_files("meeting_data/")
        
        # Check if any meeting data entries have this transcript as source
        for key in s3_meeting_data:
            if not key.endswith(".json"):
                continue
                
            meeting_data_json = storage_repo.get_file_from_s3(key)
            if meeting_data_json:
                try:
                    meeting_data = json.loads(meeting_data_json)
                    if meeting_data.get("source") == transcript_id:
                        logger.info(f"Transcript {transcript_id} already processed as meeting {meeting_data.get('id')}")
                        return {
                            "success": True,
                            "message": "Meeting data already exists for this transcript",
                            "meetingDataId": meeting_data.get("id"),
                            "alreadyProcessed": True
                        }
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse meeting data JSON: {key}")
        
        # If not already processed, continue with processing
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
        
        # Generate meeting data ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        meeting_data_id = f"meeting_{timestamp}"
        
        # Store in DynamoDB if enabled
        if settings.use_dynamodb:
            meeting_id = storage_repo.save_meeting_to_dynamodb(final_state)
            if meeting_id:
                meeting_data_id = meeting_id
                logger.info(f"Meeting saved to DynamoDB with ID: {meeting_id}")
        
        # Always save minutes and actions to S3
        # Just pass the meeting_data_id without prefixes or extensions
        # The S3 service will handle adding the proper prefix and extension
        
        # Save minutes to S3
        if storage_repo.save_minutes_s3(meeting_data_id, minutes_md):
            logger.info(f"Minutes saved to S3: minutes/{meeting_data_id}.md")
        else:
            logger.warning(f"Failed to save minutes to S3: minutes/{meeting_data_id}.md")
        
        # Save actions to S3
        if tasks:
            if not isinstance(tasks[0], dict):
                tasks_dict = [task.model_dump() for task in tasks]
            else:
                tasks_dict = tasks
                
            if storage_repo.save_actions_s3(meeting_data_id, tasks_dict):
                logger.info(f"Actions saved to S3: actions/{meeting_data_id}.json")
            else:
                logger.warning(f"Failed to save actions to S3: actions/{meeting_data_id}.json")
        
        # Save a JSON representation of the full meeting data for easy retrieval
        meeting_data = {
            "id": meeting_data_id,
            "title": final_state.get("title") if hasattr(final_state, "get") and final_state.get("title") else f"Meeting Notes: {os.path.splitext(filename)[0]}",
            "date": datetime.now().strftime("%B %d, %Y"),
            "summary": minutes_md[:500] if len(minutes_md) > 500 else minutes_md,
            "executiveSummary": final_state.get("executive_summary", "") if hasattr(final_state, "get") else "",
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
        
        # Save the complete meeting data to S3 - use clean key without double extensions
        s3_meeting_data_key = f"meeting_data/{meeting_data_id}.json"
        storage_repo.save_file_to_s3(
            s3_meeting_data_key, 
            json.dumps(meeting_data, indent=2).encode('utf-8')
        )
        logger.info(f"Complete meeting data saved to S3: {s3_meeting_data_key}")
        
        # Return success response with the meeting data ID
        return {
            "success": True,
            "message": "Meeting data generated successfully",
            "meetingDataId": meeting_data_id
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error generating meeting data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate meeting data: {str(e)}")

@app.get("/api/meeting-data/{meeting_id}")
async def get_meeting_data(meeting_id: str):
    """Get meeting data by ID"""
    try:
        # First try to get the complete meeting data JSON from S3
        s3_meeting_data_key = f"meeting_data/{meeting_id}.json"
        meeting_data_json = storage_repo.get_file_from_s3(s3_meeting_data_key)
        
        if meeting_data_json:
            # Parse the JSON data
            meeting_data = json.loads(meeting_data_json)
            
            # Log the source field for debugging
            if "source" in meeting_data:
                logger.info(f"Meeting data source field: {meeting_data['source']}")
                
                # Log if source contains a UUID
                import re
                uuid_pattern = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
                uuid_match = re.search(uuid_pattern, meeting_data['source'])
                if uuid_match:
                    logger.info(f"Source contains UUID: {uuid_match.group(1)}")
            
            # Return the pre-formatted meeting data JSON
            return meeting_data
        
        # If not found, try to get from DynamoDB
        meeting = None
        if settings.use_dynamodb:
            meeting = storage_repo.get_meeting_from_dynamodb(meeting_id)
        
        # If not found in DynamoDB, try to get from S3 minutes and actions
        if not meeting:
            # Check if minutes exist in S3
            s3_minutes_key = f"minutes/{meeting_id}.md"
            minutes_md = storage_repo.get_file_from_s3(s3_minutes_key)
            
            if not minutes_md:
                raise HTTPException(status_code=404, detail=f"Meeting data not found: {meeting_id}")
            
            # Try to get actions from S3
            s3_actions_key = f"actions/{meeting_id}.json"
            actions_json = storage_repo.get_file_from_s3(s3_actions_key)
            
            # Create a basic meeting object
            meeting = {
                "meeting_id": meeting_id,
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
        
        # Generate a concise summary if minutes_md is too long (over 800 words)
        summary = meeting.get("summary", "")
        minutes_md = meeting.get("minutes_md", "")
        
        if not summary and minutes_md:
            # Count words in minutes_md
            word_count = len(minutes_md.split())
            
            if word_count > 800:
                # For long content, create a shorter summary using just the first sections
                # This prevents truncation in the middle of a sentence
                sections = minutes_md.split("##")
                if len(sections) > 1:
                    # Use the title and first section as summary
                    summary = sections[0].strip()
                    # Add the next section if it's the agenda
                    if len(sections) > 1 and "agenda" in sections[1].lower():
                        summary += "\n## " + sections[1].strip()
                else:
                    # If no sections, use the first 800 words
                    words = minutes_md.split()
                    summary = " ".join(words[:800])
            else:
                # For shorter content, use the full minutes
                summary = minutes_md
        
        # Create response object
        meeting_data = {
            "id": meeting.get("meeting_id", meeting_id),
            "title": title,
            "date": meeting.get("date", datetime.now().strftime("%B %d, %Y")),
            "summary": summary,  # Use our carefully constructed summary
            "actionItems": action_items,
            "keyPoints": key_points,
            "participants": meeting.get("participants", []),
            "duration": meeting.get("duration", "Unknown"),
            "source": meeting.get("source", "Unknown")
        }
        
        # Save this formatted meeting data for future use
        s3_meeting_data_key = f"meeting_data/{meeting_id}.json"
        storage_repo.save_file_to_s3(
            s3_meeting_data_key, 
            json.dumps(meeting_data, indent=2).encode('utf-8')
        )
        logger.info(f"Created and saved formatted meeting data to S3: {s3_meeting_data_key}")
        
        return meeting_data
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting meeting data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get meeting data: {str(e)}")

@app.get("/api/meeting-data/list")
async def list_meeting_data():
    """List all available meeting data"""
    try:
        # Get all meeting data files from S3
        s3_meeting_data = storage_repo.list_s3_objects_with_prefix("meeting_data/")
        
        # Format the response
        meeting_data_list = []
        
        for key in s3_meeting_data:
            if not key.endswith(".json"):
                continue
                
            # Get the meeting data from S3
            meeting_data_json = storage_repo.get_file_from_s3(key)
            
            if meeting_data_json:
                meeting_data = json.loads(meeting_data_json)
                meeting_data_list.append(meeting_data)
        
        # If no meeting data found in S3, try DynamoDB
        if not meeting_data_list and settings.use_dynamodb:
            meetings = storage_repo.list_meetings_from_dynamodb()
            
            for meeting in meetings:
                meeting_data = {
                    "id": meeting.get("meeting_id", ""),
                    "title": "Meeting Summary",
                    "date": meeting.get("date", ""),
                    "participants": meeting.get("participants", []),
                    "actionItems": len(meeting.get("tasks", [])),
                    "keyPoints": len(meeting.get("agenda", [])) + len(meeting.get("decisions", [])),
                    "duration": meeting.get("duration", "Unknown")
                }
                meeting_data_list.append(meeting_data)
        
        return {"meetingData": meeting_data_list}
    
    except Exception as e:
        logger.error(f"Error listing meeting data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list meeting data: {str(e)}")

@app.get("/api/tasks/high-priority")
async def get_high_priority_tasks():
    """Get high priority tasks from all meetings"""
    try:
        high_priority_tasks = []
        
        # Get all meeting data files from S3
        s3_meeting_data = storage_repo.list_s3_objects_with_prefix("meeting_data/")
        
        for key in s3_meeting_data:
            if not key.endswith(".json"):
                continue
                
            # Get the meeting data from S3
            meeting_data_json = storage_repo.get_file_from_s3(key)
            
            if meeting_data_json:
                meeting_data = json.loads(meeting_data_json)
                meeting_id = meeting_data.get("id", "")
                
                # Extract high priority tasks
                action_items = meeting_data.get("actionItems", [])
                for item in action_items:
                    if item.get("priority", "").lower() == "high" or item.get("priority", "").lower() == "urgent":
                        task = {
                            "id": item.get("id", ""),
                            "text": item.get("text", ""),
                            "owner": item.get("owner", ""),
                            "due": item.get("due", ""),
                            "priority": "High",
                            "completed": item.get("completed", False),
                            "meetingId": meeting_id
                        }
                        high_priority_tasks.append(task)
        
        # If no tasks found in S3, try DynamoDB
        if not high_priority_tasks and settings.use_dynamodb:
            tasks = storage_repo.find_high_priority_tasks()
            
            for task in tasks:
                high_priority_task = {
                    "id": str(uuid.uuid4()),
                    "text": task.get("task", ""),
                    "owner": task.get("owner", ""),
                    "due": task.get("due", ""),
                    "priority": "High",
                    "completed": task.get("completed", False),
                    "meetingId": task.get("meeting_id", "")
                }
                high_priority_tasks.append(high_priority_task)
        
        return {"tasks": high_priority_tasks}
    
    except Exception as e:
        logger.error(f"Error getting high priority tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get high priority tasks: {str(e)}")

# Add missing import at the top of the file
import json

def run_api(port=5000):
    """Run the FastAPI server using uvicorn"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    run_api()
