"""
MAIN APPLICATION ENTRY POINT
---------------------------
This file serves as the main entry point for the Transinia application.
It provides:

1. Command-line interface for processing meeting transcripts
2. Functions to load transcripts from local files or S3 storage
3. Pipeline execution to analyze transcripts and extract information
4. Output handling to save results locally or to S3

Usage:
1. For local transcripts: python -m src
2. For S3 stored transcripts: python -m src --source s3 --s3-key your_transcript.txt
3. To list available S3 transcripts: python -m src --list-s3
"""

import os
import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Union

from src.agents.graph import create_graph
from src.config.settings import settings, logger
from src.models.schemas import MeetingState, Task
from src.repositories.storage_repo import StorageRepository
from src.utils.paths import TRANSCRIPT_TXT

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Process meeting transcripts to extract insights.")
    
    # Input options
    parser.add_argument("--file", "-f", help="Path to transcript file")
    parser.add_argument("--s3key", "-k", help="S3 key for transcript file")
    
    # Query options for DynamoDB
    parser.add_argument("--list-participants", action="store_true", help="Find all meetings by participant")
    parser.add_argument("--participant", help="Participant name to search for")
    parser.add_argument("--list-tasks", action="store_true", help="Find all tasks by owner")
    parser.add_argument("--owner", help="Task owner to search for")
    parser.add_argument("--high-priority", action="store_true", help="List all high priority tasks")
    parser.add_argument("--get-meeting", help="Get meeting by ID")
    parser.add_argument("--list-s3", action="store_true", help="List available transcripts in S3")
    parser.add_argument("--source", choices=["local", "s3"], default="local", help="Source of transcript")
    parser.add_argument("--s3-key", help="S3 key of transcript file")
    parser.add_argument("--find-meetings", help="Find meetings by participant name")
    parser.add_argument("--find-tasks", help="Find tasks by owner name")
    
    args = parser.parse_args()
    
    # Create the storage repository
    storage_repo = StorageRepository()
    
    # Handle DynamoDB query operations if requested
    if args.list_participants and args.participant:
        meetings = storage_repo.find_meetings_by_participant(args.participant)
        print(f"Found {len(meetings)} meetings with participant: {args.participant}")
        for meeting in meetings:
            print(f"Meeting ID: {meeting.get('meeting_id')}")
            print(f"Date: {meeting.get('date')}")
            print(f"Participants: {meeting.get('participants', [])}")
            print("-" * 40)
        return
    
    if args.list_tasks and args.owner:
        tasks = storage_repo.find_tasks_by_owner(args.owner)
        print(f"Found {len(tasks)} tasks for owner: {args.owner}")
        for task in tasks:
            print(f"Task: {task.get('task')}")
            print(f"Due: {task.get('due', 'No due date')}")
            print(f"Priority: {task.get('priority', 'Medium')}")
            print(f"Status: {'Completed' if task.get('completed', False) else 'Pending'}")
            print("-" * 40)
        return
    
    if args.high_priority:
        tasks = storage_repo.find_high_priority_tasks()
        print(f"Found {len(tasks)} high priority tasks")
        for task in tasks:
            print(f"Task: {task.get('task')}")
            print(f"Owner: {task.get('owner', 'Unassigned')}")
            print(f"Due: {task.get('due', 'No due date')}")
            print(f"Status: {'Completed' if task.get('completed', False) else 'Pending'}")
            print("-" * 40)
        return
    
    if args.get_meeting:
        meeting = storage_repo.get_meeting_from_dynamodb(args.get_meeting)
        if meeting:
            print(f"Meeting ID: {meeting.get('meeting_id')}")
            print(f"Date: {meeting.get('date')}")
            print(f"Participants: {meeting.get('participants', [])}")
            print(f"Agenda items: {len(meeting.get('agenda', []))}")
            print(f"Decisions: {len(meeting.get('decisions', []))}")
            print(f"Tasks: {len(meeting.get('tasks', []))}")
            print(f"Minutes:\n{meeting.get('minutes_md')}")
        else:
            print(f"No meeting found with ID: {args.get_meeting}")
        return
    
    # Handle list S3 transcripts
    if args.list_s3:
        transcripts = storage_repo.list_s3_transcripts()
        print(f"Found {len(transcripts)} transcripts in S3:")
        for key in transcripts:
            print(f"- {key}")
        return
        
    # Legacy options
    if args.find_meetings:
        meetings = storage_repo.find_meetings_by_participant(args.find_meetings)
        print(f"Found {len(meetings)} meetings with participant: {args.find_meetings}")
        for meeting in meetings:
            print(f"Meeting ID: {meeting.get('meeting_id')}")
            print(f"Date: {meeting.get('date')}")
            print(f"Participants: {meeting.get('participants', [])}")
            print("-" * 40)
        return
    
    if args.find_tasks:
        tasks = storage_repo.find_tasks_by_owner(args.find_tasks)
        print(f"Found {len(tasks)} tasks for owner: {args.find_tasks}")
        for task in tasks:
            print(f"Task: {task.get('task')}")
            print(f"Due: {task.get('due', 'No due date')}")
            print(f"Priority: {task.get('priority', 'Medium')}")
            print(f"Status: {'Completed' if task.get('completed', False) else 'Pending'}")
            print("-" * 40)
        return
    
    # Get transcript from file or S3
    transcript = ""
    source = ""
    
    if args.file:
        file_path = args.file
        logger.info(f"Reading transcript from file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            transcript = f.read()
        source = os.path.basename(file_path)
    elif args.s3key:
        s3_key = args.s3key
        logger.info(f"Reading transcript from S3: {s3_key}")
        transcript = storage_repo.get_transcript_from_s3(s3_key)
        source = s3_key
    else:
        # Use default sample transcript
        if not os.path.exists(TRANSCRIPT_TXT):
            logger.error(f"Default transcript file not found: {TRANSCRIPT_TXT}")
            return
        logger.info(f"Reading default transcript: {TRANSCRIPT_TXT}")
        with open(TRANSCRIPT_TXT, "r", encoding="utf-8") as f:
            transcript = f.read()
        source = os.path.basename(TRANSCRIPT_TXT)
    
    if not transcript:
        logger.error("No transcript content found")
        return
    
    # Create initial state
    state = MeetingState(transcript=transcript, source=source)
    
    # Create and run the processing graph
    graph = create_graph()
    logger.info("Processing transcript...")
    final_state = graph.invoke(state)
    
    # Debug - print the entire state for inspection
    logger.info(f"Final state contains: {dir(final_state)}")
    logger.info(f"Title in final state: {getattr(final_state, 'title', None) if hasattr(final_state, 'title') else final_state.get('title', None) if hasattr(final_state, 'get') else None}")
    
    # Extract values from final_state safely
    if hasattr(final_state, 'get'):
        minutes_md = final_state.get("minutes_md", "")
        agenda = final_state.get("agenda", [])
        decisions = final_state.get("decisions", [])
        tasks = final_state.get("tasks", [])
    else:
        # Handle AddableValuesDict from LangGraph
        minutes_md = getattr(final_state, "minutes_md", "")
        agenda = getattr(final_state, "agenda", [])
        decisions = getattr(final_state, "decisions", [])
        tasks = getattr(final_state, "tasks", [])
    
    # Store results
    logger.info("Storing results...")
    
    # Generate meeting ID
    meeting_id = ""
    
    # Save to DynamoDB if enabled
    if settings.use_dynamodb:
        # Make sure we're passing the complete state to DynamoDB
        meeting_id = storage_repo.save_meeting_to_dynamodb(final_state)
        if meeting_id:
            logger.info(f"Meeting saved to DynamoDB with ID: {meeting_id}")
    
    # If no meeting ID from DynamoDB, generate one
    if not meeting_id:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        meeting_id = f"meeting_{timestamp}"
    
    # Save minutes locally
    minutes_path = storage_repo.save_minutes_local(minutes_md)
    logger.info(f"Minutes saved to: {minutes_path}")
    
    # Save actions locally
    if tasks:
        # Convert tasks to dict if they are not already
        if tasks and not isinstance(tasks[0], dict):
            tasks_dict = [task.model_dump() for task in tasks]
        else:
            tasks_dict = tasks
            
        actions_path = storage_repo.save_actions_local(tasks_dict)
        logger.info(f"Actions saved to: {actions_path}")
    
    # Save to S3 if enabled
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        s3_minutes_key = f"minutes/{meeting_id}.md"
        s3_actions_key = f"actions/{meeting_id}.json"
        
        # Save minutes to S3
        if storage_repo.save_minutes_s3(s3_minutes_key, minutes_md):
            logger.info(f"Minutes saved to S3: {s3_minutes_key}")
        
        # Save actions to S3
        if tasks:
            if not isinstance(tasks[0], dict):
                tasks_dict = [task.model_dump() for task in tasks]
            else:
                tasks_dict = tasks
                
            if storage_repo.save_actions_s3(s3_actions_key, tasks_dict):
                logger.info(f"Actions saved to S3: {s3_actions_key}")
    
    # Output summary
    print("\n" + "=" * 60)
    print("MEETING SUMMARY")
    print("=" * 60)
    print(f"Meeting ID: {meeting_id}")
    print(f"Source: {source}")
    
    # Extract and display title
    title = ""
    if hasattr(final_state, 'get'):
        title = final_state.get("title", "Untitled Meeting")
    else:
        title = getattr(final_state, "title", "Untitled Meeting")
    print(f"Title: {title}")
    
    print(f"Agenda Items: {len(agenda)}")
    print(f"Decisions: {len(decisions)}")
    print(f"Action Items: {len(tasks) if tasks else 0}")
    print("=" * 60)
    print(minutes_md[:500] + "..." if len(minutes_md) > 500 else minutes_md)
    print("=" * 60)
    
    logger.info("Processing complete")

if __name__ == "__main__":
    main()
