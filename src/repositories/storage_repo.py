"""
STORAGE AND PERSISTENCE MANAGER
-----------------------------
This file handles all data persistence operations for the application.
It provides methods to:

1. Save meeting minutes as formatted Markdown files locally
2. Save action items as structured JSON files locally
3. Save meeting minutes to AWS S3 cloud storage
4. Save action items to AWS S3 cloud storage
5. Retrieve meeting transcripts from S3
6. List available transcripts in S3 storage
7. Store complete meeting data in DynamoDB
8. Retrieve and search meeting data from DynamoDB

The repository abstracts storage details away from the rest of the application,
providing a consistent interface regardless of where data is stored.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

from src.utils.paths import MINUTES_MD, ACTIONS_JSON, get_output_dir
from src.config.settings import settings, logger
from src.models.schemas import MeetingState, Task

# Import services with error handling
try:
    from src.services.s3_service import S3Service
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    logger.warning("S3Service not available. S3 storage operations will be disabled.")

try:
    from src.services.dynamodb_service import DynamoDBService
    DYNAMODB_AVAILABLE = True
except ImportError:
    DYNAMODB_AVAILABLE = False
    logger.warning("DynamoDBService not available. DynamoDB operations will be disabled.")

class StorageRepository:
    """
    Repository for saving and retrieving meeting data from various storage backends.
    """
    def __init__(self):
        """Initialize repository with available storage services."""
        self.s3_service = None
        self.dynamodb_service = None
        self.output_dir = get_output_dir()
        
        # Initialize S3 service if credentials are available
        if S3_AVAILABLE and settings.aws_access_key_id and settings.aws_secret_access_key:
            try:
                self.s3_service = S3Service()
                logger.info("S3 service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize S3 service: {str(e)}")
        
        # Initialize DynamoDB service if enabled
        if DYNAMODB_AVAILABLE and settings.use_dynamodb:
            try:
                self.dynamodb_service = DynamoDBService()
                logger.info("DynamoDB service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DynamoDB service: {str(e)}")
    
    def save_minutes_local(self, text: str) -> str:
        """Save meeting minutes to local file."""
        try:
            MINUTES_MD.parent.mkdir(parents=True, exist_ok=True)
            MINUTES_MD.write_text(text, encoding="utf-8")
            logger.info(f"Saved minutes: {MINUTES_MD}")
            return str(MINUTES_MD)
        except Exception as e:
            logger.error(f"Failed to save minutes locally: {str(e)}")
            return ""

    def save_actions_local(self, tasks: List[Dict]) -> str:
        """Save action items to local file."""
        try:
            ACTIONS_JSON.parent.mkdir(parents=True, exist_ok=True)
            ACTIONS_JSON.write_text(json.dumps({"tasks": tasks}, indent=2), encoding="utf-8")
            logger.info(f"Saved actions: {ACTIONS_JSON}")
            return str(ACTIONS_JSON)
        except Exception as e:
            logger.error(f"Failed to save actions locally: {str(e)}")
            return ""
    
    def save_minutes_s3(self, key: str, text: str) -> bool:
        """Save minutes to S3."""
        if not self.s3_service:
            logger.warning("S3 service not available. Cannot save minutes to S3.")
            return False
        
        try:
            result = self.s3_service.save_minutes(key, text)
            if result:
                logger.info(f"Saved minutes to S3: {key}")
            return result
        except Exception as e:
            logger.error(f"Failed to save minutes to S3: {str(e)}")
            return False

    def save_actions_s3(self, key: str, tasks: List[Dict]) -> bool:
        """Save actions to S3."""
        if not self.s3_service:
            logger.warning("S3 service not available. Cannot save actions to S3.")
            return False
        
        try:
            result = self.s3_service.save_actions(key, json.dumps({"tasks": tasks}, indent=2))
            if result:
                logger.info(f"Saved actions to S3: {key}")
            return result
        except Exception as e:
            logger.error(f"Failed to save actions to S3: {str(e)}")
            return False
    
    def get_transcript_from_s3(self, key: str) -> str:
        """Get transcript from S3."""
        if not self.s3_service:
            logger.warning("S3 service not available. Cannot get transcript from S3.")
            return ""
        
        try:
            transcript = self.s3_service.get_transcript(key)
            if transcript:
                logger.info(f"Retrieved transcript from S3: {key}")
            return transcript
        except Exception as e:
            logger.error(f"Failed to get transcript from S3: {str(e)}")
            return ""
    
    def list_s3_transcripts(self) -> List[str]:
        """List all transcripts in S3."""
        if not self.s3_service:
            logger.warning("S3 service not available. Cannot list S3 transcripts.")
            return []
        
        try:
            return self.s3_service.list_transcripts()
        except Exception as e:
            logger.error(f"Failed to list S3 transcripts: {str(e)}")
            return []
    
    # DynamoDB methods
    def save_meeting_to_dynamodb(self, state: Union[MeetingState, Dict[str, Any]]) -> str:
        """Save complete meeting state to DynamoDB."""
        if not self.dynamodb_service:
            logger.warning("DynamoDB service not available. Cannot save meeting to DynamoDB.")
            return ""
        
        try:
            return self.dynamodb_service.store_meeting(state)
        except Exception as e:
            logger.error(f"Failed to save meeting to DynamoDB: {str(e)}")
            return ""
    
    def get_meeting_from_dynamodb(self, meeting_id: str) -> Optional[Dict]:
        """Get complete meeting data from DynamoDB."""
        if not self.dynamodb_service:
            logger.warning("DynamoDB service not available. Cannot get meeting from DynamoDB.")
            return None
        
        try:
            return self.dynamodb_service.get_meeting(meeting_id)
        except Exception as e:
            logger.error(f"Failed to get meeting from DynamoDB: {str(e)}")
            return None
    
    def find_meetings_by_participant(self, name: str) -> List[Dict]:
        """Find meetings where a specific person participated."""
        if not self.dynamodb_service:
            logger.warning("DynamoDB service not available. Cannot find meetings by participant.")
            return []
        
        try:
            return self.dynamodb_service.find_meetings_by_participant(name)
        except Exception as e:
            logger.error(f"Failed to find meetings by participant: {str(e)}")
            return []
    
    def find_tasks_by_owner(self, owner: str) -> List[Dict]:
        """Find tasks assigned to a specific person."""
        if not self.dynamodb_service:
            logger.warning("DynamoDB service not available. Cannot find tasks by owner.")
            return []
        
        try:
            return self.dynamodb_service.find_tasks_by_owner(owner)
        except Exception as e:
            logger.error(f"Failed to find tasks by owner: {str(e)}")
            return []
    
    def find_high_priority_tasks(self) -> List[Dict]:
        """Find all high priority tasks."""
        if not self.dynamodb_service:
            logger.warning("DynamoDB service not available. Cannot find high priority tasks.")
            return []
        
        try:
            return self.dynamodb_service.find_high_priority_tasks()
        except Exception as e:
            logger.error(f"Failed to find high priority tasks: {str(e)}")
            return []
    
    def mark_task_completed(self, action_id: str, meeting_id: str, completed: bool = True) -> bool:
        """Mark a task as completed."""
        if not self.dynamodb_service:
            logger.warning("DynamoDB service not available. Cannot mark task as completed.")
            return False
        
        try:
            return self.dynamodb_service.mark_task_completed(action_id, meeting_id, completed)
        except Exception as e:
            logger.error(f"Failed to mark task as completed: {str(e)}")
            return False
    
    # Additional methods for API integration
    def save_file_to_s3(self, key: str, content: bytes) -> bool:
        """Save a file to S3."""
        if not self.s3_service:
            logger.warning("S3 service not available. Cannot save file to S3.")
            return False
        
        try:
            result = self.s3_service.save_file(key, content)
            if result:
                logger.info(f"Saved file to S3: {key}")
            return result
        except Exception as e:
            logger.error(f"Failed to save file to S3: {str(e)}")
            return False
    
    def get_file_from_s3(self, key: str) -> str:
        """Get a file from S3."""
        if not self.s3_service:
            logger.warning("S3 service not available. Cannot get file from S3.")
            return ""
        
        try:
            content = self.s3_service.get_file(key)
            if content:
                logger.info(f"Retrieved file from S3: {key}")
            return content
        except Exception as e:
            logger.error(f"Failed to get file from S3: {str(e)}")
            return ""
    
    def get_s3_object_metadata(self, key: str) -> Dict:
        """Get metadata for an S3 object."""
        if not self.s3_service:
            logger.warning("S3 service not available. Cannot get S3 object metadata.")
            return {}
        
        try:
            return self.s3_service.get_object_metadata(key)
        except Exception as e:
            logger.error(f"Failed to get S3 object metadata: {str(e)}")
            return {}
