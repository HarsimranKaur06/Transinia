# Script to add new methods to the DynamoDB service for finding tasks by due date

from src.services.dynamodb_service import DynamoDBService
from datetime import datetime, timedelta
import boto3
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('add_due_date_query')

def add_due_date_query():
    """
    Add the find_tasks_by_due_date method to the DynamoDBService class.
    This demonstrates how to add new query capabilities to the service.
    """
    # Create instance of DynamoDBService
    dynamodb_service = DynamoDBService()
    
    # Define a function to find tasks due in the next N days
    def find_tasks_by_due_date(self, days: int = 7) -> list:
        """
        Find all tasks due in the next specified number of days.
        Uses the priority-due-index GSI.
        """
        try:
            # Calculate the date range
            today = datetime.now().date()
            end_date = today + timedelta(days=days)
            
            # Format dates for query
            today_str = today.isoformat()
            end_date_str = end_date.isoformat()
            
            # Use a between condition on the priority_due key
            # This will match all priorities with due dates in our range
            response = self.actions_table.scan(
                FilterExpression="attribute_exists(due) AND due BETWEEN :start_date AND :end_date",
                ExpressionAttributeValues={
                    ':start_date': today_str,
                    ':end_date': end_date_str
                }
            )
            
            if 'Items' in response:
                tasks = response['Items']
                logger.info(f"Found {len(tasks)} tasks due in the next {days} days")
                return tasks
            return []
        except Exception as e:
            logger.error(f"Error searching tasks by due date: {e}")
            return []
    
    # Add the method to the DynamoDBService class
    setattr(DynamoDBService, 'find_tasks_by_due_date', find_tasks_by_due_date)
    
    # Test the method with an example
    today = datetime.now().date().isoformat()
    print(f"Searching for tasks due after {today}")
    tasks = dynamodb_service.find_tasks_by_due_date(14)  # Tasks due in next 2 weeks
    print(f"Found {len(tasks)} tasks due in the next 14 days")
    
    # Display task details
    for task in tasks:
        print(f"Task: {task.get('task', 'Unknown')}")
        print(f"Owner: {task.get('owner', 'Unassigned')}")
        print(f"Due: {task.get('due', 'No due date')}")
        print(f"Priority: {task.get('priority', 'Medium')}")
        print(f"Completed: {'Yes' if task.get('completed', False) else 'No'}")
        print("-" * 40)

if __name__ == "__main__":
    add_due_date_query()
