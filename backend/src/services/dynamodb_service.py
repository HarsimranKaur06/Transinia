"""
DYNAMODB STORAGE SERVICE
------------------------
This file provides integration with AWS DynamoDB for persistent storage of
meeting data. It enables:

1. Storing complete meeting records with all extracted information
2. Retrieving meetings by ID, date, participant, or other attributes
3. Searching meeting content across the entire archive
4. Tracking action items and their completion status

DynamoDB provides a scalable, high-performance database solution for
storing thousands of meeting records with millisecond retrieval times.
"""

import boto3
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.src.config.settings import settings, logger
from backend.src.models.schemas import MeetingState, Task

class DynamoDBService:
    """
    Service for interacting with DynamoDB for meeting data storage.
    """
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.meetings_table_name = settings.dynamodb_table_meetings
        self.actions_table_name = settings.dynamodb_table_actions
        self.meetings_table = self.dynamodb.Table(self.meetings_table_name)
        self.actions_table = self.dynamodb.Table(self.actions_table_name)
    
    def store_meeting(self, state):
        """
        Store a complete meeting record in DynamoDB.
        Returns the meeting_id of the stored record.
        """
        meeting_id = str(uuid.uuid4())
        today = datetime.now().isoformat()
        
        # Extract participants from transcript (enhanced implementation)
        participants = []
        participant_keys = []
        
        # Handle different types of state objects (direct attribute access or dict-like access)
        # This accommodates both Pydantic models and LangGraph's AddableValuesDict
        if hasattr(state, 'get'):
            # Dict-like access (for AddableValuesDict from LangGraph)
            agenda = state.get("agenda", [])
            decisions = state.get("decisions", [])
            minutes_md = state.get("minutes_md", "")
            source = state.get("source", "unknown")
            transcript = state.get("transcript", "")
            tasks = state.get("tasks", [])
        else:
            # Direct attribute access (for Pydantic model or similar)
            agenda = state.agenda if hasattr(state, 'agenda') else []
            decisions = state.decisions if hasattr(state, 'decisions') else []
            minutes_md = state.minutes_md if hasattr(state, 'minutes_md') else ""
            source = state.source if hasattr(state, 'source') else "unknown"
            transcript = state.transcript if hasattr(state, 'transcript') else ""
            tasks = state.tasks if hasattr(state, 'tasks') else []
        
        # Extract participants from transcript
        if transcript:
            # Try to find attendees list
            if "Attendees:" in transcript:
                attendee_line = ""
                for line in transcript.split("\n"):
                    if "Attendees:" in line:
                        attendee_line = line
                        break
                
                if attendee_line:
                    participants = [
                        name.strip() for name in 
                        attendee_line.replace("Attendees:", "").split(",")
                    ]
            
            # If no attendees list, extract participants from tasks
            if not participants and tasks:
                # Extract owners from tasks
                for task in tasks:
                    owner = task.get('owner', '') if isinstance(task, dict) else getattr(task, 'owner', '')
                    if owner and owner not in participants:
                        participants.append(owner)
            
            # Create participant keys for searching
            participant_keys = [f"PARTICIPANT#{name.strip().lower()}" for name in participants]
        
        # Prepare tasks for storage
        task_dicts = []
        if tasks:
            # Check if tasks is already a list of dicts or a list of Task objects
            if isinstance(tasks, list) and len(tasks) > 0:
                if isinstance(tasks[0], dict):
                    task_dicts = tasks
                else:
                    task_dicts = [task.model_dump() for task in tasks]
                
                # Also store individual tasks in the actions table
                self._store_tasks(meeting_id, today, task_dicts)
        
        # Create item for DynamoDB meetings table
        item = {
            'meeting_id': meeting_id,
            'date': today,
            'transcript': transcript,
            'minutes_md': minutes_md,
            'agenda': agenda,
            'decisions': decisions,
            'tasks': task_dicts,
            'participants': participants,
            'participant_key': participant_keys[0] if participant_keys else "PARTICIPANT#unknown",
            'metadata': {
                'source': source,
                'created_at': today
            }
        }
        
        try:
            self.meetings_table.put_item(Item=item)
            logger.info(f"Meeting stored in DynamoDB with ID: {meeting_id}")
            return meeting_id
        except Exception as e:
            logger.error(f"Error storing meeting in DynamoDB: {e}")
            return ""
            
    def _store_tasks(self, meeting_id: str, meeting_date: str, tasks: List[Dict]) -> None:
        """
        Store individual tasks in the actions table for easier querying.
        """
        for task in tasks:
            task_id = str(uuid.uuid4())
            owner = task.get('owner', 'Unassigned')
            due_date = task.get('due', '')
            
            # Ensure consistent priority formatting (High, Med, Low)
            priority_raw = task.get('priority', 'Med')
            # Normalize priority to capitalized format (High, Med, Low)
            if priority_raw.upper() == "HIGH":
                priority = "High"
            elif priority_raw.upper() == "LOW":
                priority = "Low"
            else:
                priority = "Med"
            
            try:
                self.actions_table.put_item(Item={
                    'action_id': task_id,
                    'meeting_id': meeting_id,
                    'meeting_date': meeting_date,
                    'task': task.get('task', ''),
                    'owner': owner,
                    'due': due_date,
                    'priority': priority,
                    'completed': False
                })
            except Exception as e:
                logger.error(f"Error storing task in DynamoDB actions table: {e}")
    
    def get_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a meeting by its ID.
        """
        try:
            # First try to find the meeting using a scan with a filter on meeting_id
            # This is more flexible but less efficient
            response = self.meetings_table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('meeting_id').eq(meeting_id)
            )
            
            if 'Items' in response and len(response['Items']) > 0:
                # Process the items to ensure all expected fields are present
                meeting_data = response['Items'][0]
                
                # Ensure all expected fields have at least default values
                if 'agenda' not in meeting_data:
                    meeting_data['agenda'] = []
                if 'decisions' not in meeting_data:
                    meeting_data['decisions'] = []
                if 'tasks' not in meeting_data:
                    meeting_data['tasks'] = []
                if 'participants' not in meeting_data:
                    meeting_data['participants'] = []
                if 'minutes_md' not in meeting_data:
                    meeting_data['minutes_md'] = ""
                
                logger.info(f"Meeting retrieved from DynamoDB: {meeting_id}")
                return meeting_data
            
            # If not found with scan, try the direct key query (original approach)
            # This would work if we knew the date value for the range key
            try:
                # Try to query the table with just the hash key and let DynamoDB scan the range
                response = self.meetings_table.query(
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('meeting_id').eq(meeting_id)
                )
                
                if 'Items' in response and len(response['Items']) > 0:
                    meeting_data = response['Items'][0]
                    
                    # Ensure all expected fields have at least default values
                    if 'agenda' not in meeting_data:
                        meeting_data['agenda'] = []
                    if 'decisions' not in meeting_data:
                        meeting_data['decisions'] = []
                    if 'tasks' not in meeting_data:
                        meeting_data['tasks'] = []
                    if 'participants' not in meeting_data:
                        meeting_data['participants'] = []
                    if 'minutes_md' not in meeting_data:
                        meeting_data['minutes_md'] = ""
                    
                    logger.info(f"Meeting retrieved from DynamoDB: {meeting_id}")
                    return meeting_data
            except Exception as inner_e:
                logger.debug(f"Query operation failed: {inner_e}")
            
            logger.warning(f"Meeting not found in DynamoDB: {meeting_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving meeting from DynamoDB: {e}")
            return None
    
    def find_meetings_by_participant(self, name: str) -> List[Dict[str, Any]]:
        """
        Find all meetings where a specific person participated.
        First tries GSI on participant-index, then falls back to scanning the participants list.
        """
        try:
            meetings = []
            # Format the participant key in the same way it's stored
            participant_key = f"PARTICIPANT#{name.lower()}"
            
            # First try using the GSI
            try:
                response = self.meetings_table.query(
                    IndexName='participant-index',
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('participant_key').eq(participant_key)
                )
                
                if 'Items' in response:
                    meetings.extend(response['Items'])
            except Exception as e:
                logger.debug(f"Error querying participant-index GSI: {e}")
            
            # If GSI query didn't yield results, try scanning the participants list
            if not meetings:
                response = self.meetings_table.scan(
                    FilterExpression=boto3.dynamodb.conditions.Attr('participants').contains(name)
                )
                
                if 'Items' in response:
                    meetings.extend(response['Items'])
            
            # Deduplicate meetings (in case the same meeting was found by both methods)
            unique_meetings = {}
            for meeting in meetings:
                meeting_id = meeting.get('meeting_id', '')
                if meeting_id:
                    unique_meetings[meeting_id] = meeting
            
            result = list(unique_meetings.values())
            logger.info(f"Found {len(result)} meetings with participant: {name}")
            return result
        except Exception as e:
            logger.error(f"Error searching meetings by participant: {e}")
            return []
    
    def find_tasks_by_owner(self, owner: str) -> List[Dict[str, Any]]:
        """
        Find all tasks assigned to a specific person across all meetings.
        Uses the owner-index GSI on the actions table.
        """
        try:
            response = self.actions_table.query(
                IndexName='owner-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('owner').eq(owner)
            )
            
            if 'Items' in response:
                tasks = response['Items']
                logger.info(f"Found {len(tasks)} tasks for owner: {owner}")
                return tasks
            return []
        except Exception as e:
            logger.error(f"Error searching tasks by owner: {e}")
            return []
    
    def find_high_priority_tasks(self) -> List[Dict[str, Any]]:
        """
        Find all high priority tasks.
        Uses a scan operation with a filter on priority="High".
        """
        try:
            # Use scan with filter expression instead of a query
            filter_expression = boto3.dynamodb.conditions.Attr('priority').eq('High')
            
            response = self.actions_table.scan(
                FilterExpression=filter_expression
            )
            
            if 'Items' in response:
                tasks = response['Items']
                logger.info(f"Found {len(tasks)} high priority tasks")
                return tasks
            return []
        except Exception as e:
            logger.error(f"Error searching high priority tasks: {e}")
            return []
    
    def mark_task_completed(self, action_id: str, meeting_id: str, completed: bool = True) -> bool:
        """
        Mark a task as completed or not completed.
        """
        try:
            self.actions_table.update_item(
                Key={
                    'action_id': action_id,
                    'meeting_id': meeting_id
                },
                UpdateExpression="SET completed = :completed",
                ExpressionAttributeValues={
                    ':completed': completed
                }
            )
            status = "completed" if completed else "incomplete"
            logger.info(f"Task {action_id} marked as {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating task completion status: {e}")
            return False
            
    def list_meetings(self) -> List[Dict[str, Any]]:
        """
        List all meetings in the database.
        Uses a scan operation with no filter to retrieve all meetings.
        """
        try:
            response = self.meetings_table.scan()
            if 'Items' in response:
                meetings = response['Items']
                logger.info(f"Found {len(meetings)} meetings")
                return meetings
            return []
        except Exception as e:
            logger.error(f"Error listing meetings: {e}")
            return []
