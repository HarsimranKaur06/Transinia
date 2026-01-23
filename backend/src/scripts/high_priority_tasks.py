"""
List high priority tasks from DynamoDB
"""

from src.repositories.storage_repo import StorageRepository

def main():
    storage_repo = StorageRepository()
    tasks = storage_repo.find_high_priority_tasks()
    
    print(f"Found {len(tasks)} high priority tasks")
    for task in tasks:
        print(f"Task: {task.get('task')}")
        print(f"Owner: {task.get('owner', 'Unassigned')}")
        print(f"Due: {task.get('due', 'No due date')}")
        print(f"Status: {'Completed' if task.get('completed', False) else 'Pending'}")
        print("-" * 40)

if __name__ == "__main__":
    main()
