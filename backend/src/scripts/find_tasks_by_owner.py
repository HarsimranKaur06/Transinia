"""
Find tasks by owner from DynamoDB
"""

import sys
from src.repositories.storage_repo import StorageRepository

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.find_tasks_by_owner <owner_name>")
        return
        
    owner = sys.argv[1]
    storage_repo = StorageRepository()
    tasks = storage_repo.find_tasks_by_owner(owner)
    
    print(f"Found {len(tasks)} tasks for owner: {owner}")
    for task in tasks:
        print(f"Task: {task.get('task')}")
        print(f"Due: {task.get('due', 'No due date')}")
        print(f"Priority: {task.get('priority', 'Medium')}")
        print(f"Status: {'Completed' if task.get('completed', False) else 'Pending'}")
        print("-" * 40)

if __name__ == "__main__":
    main()
