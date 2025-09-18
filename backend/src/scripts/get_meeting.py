"""
Get a meeting by ID from DynamoDB
"""

import sys
from src.repositories.storage_repo import StorageRepository

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.get_meeting <meeting_id>")
        return
        
    meeting_id = sys.argv[1]
    storage_repo = StorageRepository()
    meeting = storage_repo.get_meeting_from_dynamodb(meeting_id)
    
    if meeting:
        print(f"Meeting ID: {meeting.get('meeting_id')}")
        print(f"Date: {meeting.get('date')}")
        print(f"Participants: {meeting.get('participants', [])}")
        print(f"Agenda items: {len(meeting.get('agenda', []))}")
        print(f"Decisions: {len(meeting.get('decisions', []))}")
        print(f"Tasks: {len(meeting.get('tasks', []))}")
        print("\nMinutes:")
        print("-" * 40)
        print(meeting.get('minutes_md'))
    else:
        print(f"No meeting found with ID: {meeting_id}")

if __name__ == "__main__":
    main()
