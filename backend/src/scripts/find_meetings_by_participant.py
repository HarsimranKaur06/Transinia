"""
Find meetings by participant from DynamoDB
"""

import sys
from src.repositories.storage_repo import StorageRepository

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.find_meetings_by_participant <participant_name>")
        return
        
    participant = sys.argv[1]
    storage_repo = StorageRepository()
    meetings = storage_repo.find_meetings_by_participant(participant)
    
    print(f"Found {len(meetings)} meetings with participant: {participant}")
    for meeting in meetings:
        print(f"Meeting ID: {meeting.get('meeting_id')}")
        print(f"Date: {meeting.get('date')}")
        print(f"Participants: {meeting.get('participants', [])}")
        print("-" * 40)

if __name__ == "__main__":
    main()
