# Example script showing how to use DynamoDB services in Transinia

import os
import sys
import logging
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.dynamodb_service import DynamoDBService
from src.models.schemas import MeetingState, Task
from src.config.settings import settings

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('dynamodb_examples')

def example_dynamodb_usage():
    """
    Example of using the DynamoDB service to store and retrieve meeting data.
    This demonstrates the full capabilities of the DynamoDB integration.
    """
    # Create a DynamoDB service instance
    dynamodb = DynamoDBService()
    
    # 1. Create sample meeting data
    logger.info("Creating sample meeting data...")
    sample_meeting = MeetingState(
        transcript="Attendees: Alice Smith, Bob Johnson, Carol Williams\n\nMeeting to discuss Q3 planning.",
        minutes_md="# Q3 Planning Meeting\n\n## Agenda\n1. Budget review\n2. Hiring plan\n3. Project timeline\n\n## Decisions\n- Approved $50k budget for new marketing campaign\n- Agreed to hire 2 new developers by August\n\n## Action Items\n- Alice: Prepare marketing budget breakdown by July 15\n- Bob: Finalize job descriptions by next week\n- Carol: Update project timeline with new milestones",
        agenda=["Budget review", "Hiring plan", "Project timeline"],
        decisions=[
            "Approved $50k budget for new marketing campaign",
            "Agreed to hire 2 new developers by August"
        ],
        tasks=[
            Task(
                task="Prepare marketing budget breakdown", 
                owner="Alice Smith", 
                due="2023-07-15", 
                priority="High"
            ),
            Task(
                task="Finalize job descriptions", 
                owner="Bob Johnson", 
                due="2023-07-07", 
                priority="Medium"
            ),
            Task(
                task="Update project timeline with new milestones", 
                owner="Carol Williams", 
                due="2023-07-20", 
                priority="Medium"
            )
        ],
        source="sample_data"
    )
    
    # 2. Store the meeting in DynamoDB
    logger.info("Storing meeting in DynamoDB...")
    meeting_id = dynamodb.store_meeting(sample_meeting)
    logger.info(f"Meeting stored with ID: {meeting_id}")
    
    # 3. Retrieve the meeting from DynamoDB
    logger.info("Retrieving meeting from DynamoDB...")
    meeting = dynamodb.get_meeting(meeting_id)
    if meeting:
        logger.info(f"Retrieved meeting: {meeting['meeting_id']}")
        logger.info(f"Meeting date: {meeting['date']}")
        logger.info(f"Participants: {meeting.get('participants', [])}")
        logger.info(f"Number of agenda items: {len(meeting.get('agenda', []))}")
        logger.info(f"Number of decisions: {len(meeting.get('decisions', []))}")
        logger.info(f"Number of tasks: {len(meeting.get('tasks', []))}")
    
    # 4. Find meetings by participant
    logger.info("Finding meetings with participant 'Alice Smith'...")
    alice_meetings = dynamodb.find_meetings_by_participant("Alice Smith")
    logger.info(f"Found {len(alice_meetings)} meetings with Alice")
    
    # 5. Find tasks for Bob
    logger.info("Finding tasks assigned to 'Bob Johnson'...")
    bob_tasks = dynamodb.find_tasks_by_owner("Bob Johnson")
    logger.info(f"Found {len(bob_tasks)} tasks for Bob")
    for task in bob_tasks:
        logger.info(f"  - Task: {task.get('task')}, Due: {task.get('due')}")
    
    # 6. Find high priority tasks
    logger.info("Finding high priority tasks...")
    high_priority = dynamodb.find_high_priority_tasks()
    logger.info(f"Found {len(high_priority)} high priority tasks")
    for task in high_priority:
        logger.info(f"  - Task: {task.get('task')}, Owner: {task.get('owner')}, Due: {task.get('due')}")
    
    # 7. Mark a task as completed (if we found any tasks for Bob)
    if bob_tasks:
        first_task = bob_tasks[0]
        logger.info(f"Marking task '{first_task.get('task')}' as completed...")
        result = dynamodb.mark_task_completed(
            first_task.get('action_id'), 
            first_task.get('meeting_id')
        )
        if result:
            logger.info("Task marked as completed successfully")
    
    logger.info("DynamoDB example operations completed")

if __name__ == "__main__":
    # Check if DynamoDB settings are configured
    if not settings.use_dynamodb:
        logger.warning("DynamoDB is not enabled in settings. Setting to True for this example.")
        settings.use_dynamodb = True
    
    if not settings.aws_access_key_id or not settings.aws_secret_access_key:
        logger.error("AWS credentials not found in settings. Please configure your .env file.")
        sys.exit(1)
    
    if not settings.dynamodb_table_meetings or not settings.dynamodb_table_actions:
        logger.error("DynamoDB table names not found in settings. Please configure your .env file.")
        sys.exit(1)
    
    # Run the example
    example_dynamodb_usage()
